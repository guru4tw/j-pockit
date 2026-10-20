# j-pockit installer: flat-install pstack + mattpocock-skills into ~/.claude/skills/<name>/.
# Spec: docs/spec/j-pockit-spec.md. ASCII-only; run _Owlery/parse_ps1.ps1 after every edit.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1           # install exactly what versions.lock pins
#   powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1 -Update   # bump versions.lock to upstream latest, then install
#   powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1 -UserOnly pr,wizard
#       # after install, add 'disable-model-invocation: true' to these SKILL.md files (only you can call them)

param(
    [switch]$Update,
    [string[]]$UserOnly = @()
)

$ErrorActionPreference = 'Stop'

# -File passes "a,b" as one string; split it here.
$UserOnly = @($UserOnly | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim().TrimStart('/') } | Where-Object { $_ })

# Model-callable skills that can become user-only without breaking a skill chain.
# prototype / research: only /wayfinder calls them; safe if you never use /wayfinder.
# Never allowed: grilling, domain-modeling, tdd, code-review, codebase-design, writing-for-agents
# (Pocock entry skills call them through the Skill tool, which refuses user-only skills).
$UserOnlyAllowed = @('setup-pstack', 'diagnosing-bugs', 'wizard', 'pr', 'prototype', 'research')

# --- Exclusions (same-name conflicts) ---
$PstackExclude = @(
    'tdd'        # Pocock tdd wins: Pocock /implement calls /tdd
)
$PocockExclude = @(
    'teach',     # pstack teach wins
    'handoff'    # a skill beats a same-name command; would shadow ~/.claude/commands/handoff.md (Stop hook /handoff)
)

# --- Upstreams ---
$PstackUrl     = 'https://github.com/cursor/plugins'
$PstackBranch  = 'main'
$PstackSubdir  = 'harness/pstack/claude-code'
$PocockUrl     = 'https://github.com/mattpocock/skills'
$PocockSubdirs = @('skills/engineering', 'skills/productivity')

$LockPath     = Join-Path $PSScriptRoot 'versions.lock'
$ClaudeDir    = Join-Path $HOME '.claude'
$SkillsDir    = Join-Path $ClaudeDir 'skills'
$DocsDir      = Join-Path $ClaudeDir 'docs'
$AgentsDir    = Join-Path $ClaudeDir 'agents'
$ArchiveRoot  = Join-Path $ClaudeDir 'skills_archive'
$ManifestPath = Join-Path $ClaudeDir 'j-pockit-installed.txt'   # names installed last run, for the "removed upstream" hint
$TempRoot     = Join-Path $env:TEMP 'j-pockit'

function Fail([string]$Message) {
    [Console]::Error.WriteLine("ERROR: $Message")
    exit 1
}

function Invoke-Git([string[]]$GitArgs) {
    $out = & git @GitArgs
    if ($LASTEXITCODE -ne 0) { Fail "git $($GitArgs -join ' ') failed (exit $LASTEXITCODE)" }
    return $out
}

function Read-Lock {
    if (-not (Test-Path -LiteralPath $LockPath)) { Fail "versions.lock not found: $LockPath" }
    $lock = @{}
    foreach ($line in Get-Content -LiteralPath $LockPath) {
        if ($line -match '^\s*([^=\s]+)\s*=\s*(\S+)\s*$') { $lock[$Matches[1]] = $Matches[2] }
    }
    if (-not $lock.ContainsKey('pstack'))            { Fail "versions.lock has no 'pstack=' line" }
    if (-not $lock.ContainsKey('mattpocock-skills')) { Fail "versions.lock has no 'mattpocock-skills=' line" }
    if ($lock['pstack'] -notmatch '^[0-9a-f]{40}$')  { Fail "versions.lock pstack must be a full 40-char commit SHA, got '$($lock['pstack'])'" }
    return $lock
}

function Write-Lock([string]$PstackSha, [string]$PocockTag) {
    $text = "pstack=$PstackSha`nmattpocock-skills=$PocockTag`n"
    [IO.File]::WriteAllText($LockPath, $text, (New-Object Text.UTF8Encoding $false))
}

function Get-LatestPstackSha {
    $line = Invoke-Git @('ls-remote', $PstackUrl, "refs/heads/$PstackBranch")
    if (-not $line) { Fail "ls-remote returned nothing for $PstackUrl $PstackBranch" }
    return ([string]$line).Split("`t")[0]
}

function Get-LatestPocockTag {
    $lines = Invoke-Git @('ls-remote', '--tags', '--refs', $PocockUrl)
    $best = $null
    foreach ($l in $lines) {
        if ($l -match 'refs/tags/(v(\d+\.\d+\.\d+))$') {
            $v = [version]$Matches[2]
            if (($null -eq $best) -or ($v -gt $best.Version)) { $best = @{ Tag = $Matches[1]; Version = $v } }
        }
    }
    if ($null -eq $best) { Fail "no vX.Y.Z tag found on $PocockUrl" }
    return $best.Tag
}

# Shallow, blobless, sparse fetch of one ref. A plain --depth 1 clone only has the default
# branch tip, so a pinned SHA / tag is fetched explicitly.
function Get-Upstream([string]$Url, [string]$Ref, [string[]]$SparsePaths, [string]$Dest) {
    New-Item -ItemType Directory -Path $Dest -Force | Out-Null
    Invoke-Git @('-C', $Dest, 'init', '--quiet') | Out-Null
    Invoke-Git @('-C', $Dest, 'config', 'core.autocrlf', 'false') | Out-Null   # keep upstream bytes as-is
    Invoke-Git @('-C', $Dest, 'remote', 'add', 'origin', $Url) | Out-Null
    Invoke-Git (@('-C', $Dest, 'sparse-checkout', 'set') + $SparsePaths) | Out-Null
    Invoke-Git @('-C', $Dest, 'fetch', '--quiet', '--depth', '1', '--filter=blob:none', 'origin', $Ref) | Out-Null
    Invoke-Git @('-C', $Dest, 'checkout', '--quiet', 'FETCH_HEAD') | Out-Null
}

function Get-SkillDirs([string]$Dir, [string[]]$Exclude) {
    if (-not (Test-Path -LiteralPath $Dir)) { Fail "upstream directory missing: $Dir" }
    return @(Get-ChildItem -LiteralPath $Dir -Directory | Where-Object { $Exclude -notcontains $_.Name })
}

# Archive dir is picked once per run: <date>, then <date>-2, <date>-3 ... if taken.
$script:ArchiveDir = $null
function Get-ArchiveDir {
    if ($null -eq $script:ArchiveDir) {
        $date = Get-Date -Format 'yyyy-MM-dd'
        $candidate = Join-Path $ArchiveRoot $date
        $n = 2
        while (Test-Path -LiteralPath $candidate) {
            $candidate = Join-Path $ArchiveRoot "$date-$n"
            $n++
        }
        New-Item -ItemType Directory -Path $candidate -Force | Out-Null
        $script:ArchiveDir = $candidate
    }
    return $script:ArchiveDir
}

$Archived = New-Object System.Collections.Generic.List[string]

function Install-Skill([System.IO.DirectoryInfo]$Src) {
    $dst = Join-Path $SkillsDir $Src.Name
    if (Test-Path -LiteralPath $dst) {
        $arch = Join-Path (Get-ArchiveDir) $Src.Name
        Move-Item -LiteralPath $dst -Destination $arch
        $Archived.Add($arch)
    }
    Copy-Item -LiteralPath $Src.FullName -Destination $dst -Recurse
}

# Insert 'disable-model-invocation: true' as the first frontmatter line. Returns $false if already set.
function Set-UserOnly([string]$Name) {
    $path = Join-Path (Join-Path $SkillsDir $Name) 'SKILL.md'
    if (-not (Test-Path -LiteralPath $path)) { Fail "-UserOnly: $path not found" }
    $text = [IO.File]::ReadAllText($path)
    if ($text -notmatch '^---\r?\n') { Fail "-UserOnly: $path has no YAML frontmatter" }
    $end = $text.IndexOf("`n---", 3)
    if ($end -lt 0) { Fail "-UserOnly: $path frontmatter is not closed" }
    if ($text.Substring(0, $end) -match '(?m)^disable-model-invocation:\s*true\s*$') { return $false }
    $nl = if ($text.StartsWith("---`r`n")) { "`r`n" } else { "`n" }
    $first = $text.IndexOf("`n") + 1
    $new = $text.Substring(0, $first) + "disable-model-invocation: true$nl" + $text.Substring($first)
    [IO.File]::WriteAllText($path, $new, (New-Object Text.UTF8Encoding $false))
    return $true
}

# --- Preflight: fail before touching anything ---
$badUserOnly = @($UserOnly | Where-Object { $UserOnlyAllowed -notcontains $_ })
if ($badUserOnly.Count -gt 0) {
    Fail "-UserOnly does not accept: $($badUserOnly -join ', '). Allowed: $($UserOnlyAllowed -join ', ') (others would break a skill chain)"
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Fail 'git not found in PATH' }
if (-not (Test-Path -LiteralPath $ClaudeDir)) { Fail "$ClaudeDir does not exist" }
$lock = Read-Lock

if ($Update) {
    $newSha = Get-LatestPstackSha
    $newTag = Get-LatestPocockTag
    Write-Lock $newSha $newTag
    Write-Host "versions.lock: pstack $($lock['pstack']) -> $newSha"
    Write-Host "versions.lock: mattpocock-skills $($lock['mattpocock-skills']) -> $newTag"
    $lock = Read-Lock
}

$pstackRef = $lock['pstack']
$pocockRef = "refs/tags/$($lock['mattpocock-skills'])"

if (Test-Path -LiteralPath $TempRoot) { Remove-Item -LiteralPath $TempRoot -Recurse -Force }
try {
    $pstackTmp = Join-Path $TempRoot 'pstack'
    $pocockTmp = Join-Path $TempRoot 'mattpocock-skills'
    Write-Host "Fetching pstack @ $pstackRef ..."
    Get-Upstream $PstackUrl $pstackRef @($PstackSubdir) $pstackTmp
    Write-Host "Fetching mattpocock-skills @ $($lock['mattpocock-skills']) ..."
    Get-Upstream $PocockUrl $pocockRef $PocockSubdirs $pocockTmp

    $pstackRoot   = Join-Path $pstackTmp ($PstackSubdir -replace '/', '\')
    $pstackSkills = Get-SkillDirs (Join-Path $pstackRoot 'skills') $PstackExclude
    $pocockSkills = @()
    foreach ($sub in $PocockSubdirs) {
        $pocockSkills += Get-SkillDirs (Join-Path $pocockTmp ($sub -replace '/', '\')) $PocockExclude
    }
    if ($pstackSkills.Count -eq 0) { Fail 'pstack: 0 skills found upstream' }
    if ($pocockSkills.Count -eq 0) { Fail 'mattpocock-skills: 0 skills found upstream' }

    # A name in both sets is a new conflict the exclusion lists do not decide yet.
    $pstackNames = @($pstackSkills | ForEach-Object { $_.Name })
    $pocockNames = @($pocockSkills | ForEach-Object { $_.Name })
    $clash = @($pocockNames | Where-Object { $pstackNames -contains $_ })
    if ($clash.Count -gt 0) { Fail "same-name skill in both sets, add one side to an exclusion list: $($clash -join ', ')" }
    $dupPocock = @($pocockNames | Group-Object | Where-Object { $_.Count -gt 1 } | ForEach-Object { $_.Name })
    if ($dupPocock.Count -gt 0) { Fail "same-name skill in two mattpocock-skills folders: $($dupPocock -join ', ')" }

    # --- Install ---
    New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null
    foreach ($s in $pstackSkills) { Install-Skill $s }
    foreach ($s in $pocockSkills) { Install-Skill $s }

    # pstack docs/ -> ~/.claude/docs/ (overwrite same path, never delete, no archive)
    $docsSrc = Join-Path $pstackRoot 'docs'
    $docsCount = 0
    foreach ($f in Get-ChildItem -LiteralPath $docsSrc -Recurse -File) {
        $rel = $f.FullName.Substring($docsSrc.Length).TrimStart('\')
        $dst = Join-Path $DocsDir $rel
        New-Item -ItemType Directory -Path (Split-Path $dst -Parent) -Force | Out-Null
        Copy-Item -LiteralPath $f.FullName -Destination $dst -Force
        $docsCount++
    }

    # pstack agents/ -> ~/.claude/agents/ (same-name file archived first)
    $agentsSrc = Join-Path $pstackRoot 'agents'
    $agentNames = @()
    New-Item -ItemType Directory -Path $AgentsDir -Force | Out-Null
    foreach ($f in Get-ChildItem -LiteralPath $agentsSrc -File) {
        $dst = Join-Path $AgentsDir $f.Name
        if (Test-Path -LiteralPath $dst) {
            $archAgents = Join-Path (Get-ArchiveDir) 'agents'
            New-Item -ItemType Directory -Path $archAgents -Force | Out-Null
            $arch = Join-Path $archAgents $f.Name
            Move-Item -LiteralPath $dst -Destination $arch
            $Archived.Add($arch)
        }
        Copy-Item -LiteralPath $f.FullName -Destination $dst
        $agentNames += $f.Name
    }

    # Upstream-removed skills: never deleted, only reported.
    $installed = @($pstackNames + $pocockNames | Sort-Object)
    $stale = @()
    if (Test-Path -LiteralPath $ManifestPath) {
        foreach ($name in Get-Content -LiteralPath $ManifestPath) {
            if ($name -and ($installed -notcontains $name) -and (Test-Path -LiteralPath (Join-Path $SkillsDir $name))) { $stale += $name }
        }
    }
    [IO.File]::WriteAllText($ManifestPath, (($installed -join "`n") + "`n"), (New-Object Text.UTF8Encoding $false))

    # Optional: make chosen skills user-only. Upstream files are fresh copies, so this reruns every install.
    $userOnlyDone = @()
    foreach ($name in $UserOnly) {
        if ($installed -notcontains $name) { Fail "-UserOnly: '$name' is not in this install" }
        [void](Set-UserOnly $name)
        $userOnlyDone += $name
    }

    # --- Report ---
    Write-Host ''
    Write-Host "pstack @ $($lock['pstack']): installed $($pstackSkills.Count) skills (excluded: $($PstackExclude -join ', '))"
    Write-Host "mattpocock-skills @ $($lock['mattpocock-skills']): installed $($pocockSkills.Count) skills (excluded: $($PocockExclude -join ', '))"
    Write-Host "docs: $docsCount files copied to $DocsDir"
    Write-Host "agents: $($agentNames -join ', ') copied to $AgentsDir"
    if ($userOnlyDone.Count -gt 0) {
        Write-Host "user-only (disable-model-invocation: true): $($userOnlyDone -join ', '). Pass the same -UserOnly on every reinstall."
    } else {
        Write-Host 'user-only: none (SKILL.md files unchanged)'
    }
    if ($Archived.Count -gt 0) {
        Write-Host "archived $($Archived.Count):"
        foreach ($a in $Archived) { Write-Host "  $a" }
    } else {
        Write-Host 'archived: none'
    }
    foreach ($name in $stale) {
        Write-Host "no longer upstream, left in place (remove it yourself if unwanted): $(Join-Path $SkillsDir $name)"
    }
    Write-Host ''
    Write-Host 'v1.3 renamed CONTEXT.md to GLOSSARY.md; rename old project CONTEXT.md files yourself.'
    Write-Host 'Next: run /setup-pstack once per machine, /setup-matt-pocock-skills once per repo.'
}
finally {
    if (Test-Path -LiteralPath $TempRoot) { Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue }
}
