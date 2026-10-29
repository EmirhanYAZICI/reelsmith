# Reelsmith installer for Windows PowerShell.
#
#   .\install.ps1                         install deps + skills for every agent found on this machine
#   .\install.ps1 -Agents claude,cursor
#   .\install.ps1 -Agents all -Project    install into the current project folder instead of your home
#   & ([scriptblock]::Create((irm https://raw.githubusercontent.com/EmirhanYAZICI/reelsmith/main/install.ps1)))
#
# Options:
#   -Agents auto|all|claude,codex,opencode,cursor,antigravity   (default: auto = agents found on this machine)
#   -Project       install skills into .\.claude\skills, .\.cursor\skills ... of the current folder
#   -OM <path>     OpenMontage folder (default: $env:OPENMONTAGE_DIR or ~\Projects\OpenMontage)
#   -SkillsOnly    copy the skills, skip dependencies
#   -NoHfSkills    skip "npx hyperframes skills"
#   -NoBackup      replace changed skill folders without keeping a backup copy
#   -DryRun        show what would happen, change nothing
#
# Existing reelsmith / whisper-tr folders are left alone when identical. When they differ,
# the old copy is moved to ~\.reelsmith-backups\<time>\<agent>\ before the new one is copied.
# Python must be 3.10-3.12 (faster-whisper); other versions stop the install with a message.
param(
    [string[]]$Agents = @('auto'),
    [switch]$Project,
    [string]$OM = $(if ($env:OPENMONTAGE_DIR) { $env:OPENMONTAGE_DIR } else { Join-Path $HOME 'Projects\OpenMontage' }),
    [switch]$SkillsOnly,
    [switch]$NoHfSkills,
    [switch]$NoBackup,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'

$RepoUrl = 'https://github.com/EmirhanYAZICI/reelsmith'
$OmUrl = 'https://github.com/calesthio/OpenMontage'
$Skills = @('reelsmith', 'whisper-tr')
$AllAgents = @('claude', 'codex', 'opencode', 'cursor', 'antigravity')

function Say($m) { Write-Host "`n== $m" }
function Ok($m) { Write-Host "   ok    $m" }
function Warn($m) { Write-Host "   WARN  $m" -ForegroundColor Yellow }
function Has($c) { [bool](Get-Command $c -ErrorAction SilentlyContinue) }
# faster-whisper needs Python 3.10 - 3.12
function PyVer([string[]]$cmd) {
    try {
        $exe, $rest = $cmd
        $v = & $exe @rest -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and $v) { return "$v".Trim() }
    } catch {}
    return $null
}
function PyOk($v) { $v -and ([version]$v -ge [version]'3.10') -and ([version]$v -le [version]'3.12') }
function Run([scriptblock]$b) {
    if ($DryRun) { Write-Host "   would run: $b" } else { & $b; if ($LASTEXITCODE) { throw "failed: $b" } }
}

# Repo source: the folder this script is in, or a fresh clone when run from the web.
$Src = $PSScriptRoot
if (-not $Src -or -not (Test-Path (Join-Path $Src 'skills\reelsmith\SKILL.md'))) {
    $Src = if ($env:REELSMITH_HOME) { $env:REELSMITH_HOME } else { Join-Path $HOME '.reelsmith' }
    Say "Getting Reelsmith into $Src"
    if (Test-Path (Join-Path $Src '.git')) { Run { git -C $Src pull --ff-only } }
    else { $ref = if ($env:REELSMITH_REF) { $env:REELSMITH_REF } else { 'main' }; Run { git clone --depth 1 --branch $ref $RepoUrl $Src } }
}

function AgentDir($a) {
    $base = if ($Project) { (Get-Location).Path } else { $HOME }
    $rel = if ($Project) {
        @{ claude = '.claude\skills'; codex = '.codex\skills'; opencode = '.opencode\skills'; cursor = '.cursor\skills'; antigravity = '.agent\skills' }[$a]
    } else {
        @{ claude = '.claude\skills'; codex = '.codex\skills'; opencode = '.config\opencode\skills'; cursor = '.cursor\skills'; antigravity = '.gemini\antigravity\skills' }[$a]
    }
    if ($rel) { Join-Path $base $rel }
}
function AgentFound($a) {
    switch ($a) {
        'claude' { (Test-Path "$HOME\.claude") -or (Has claude) }
        'codex' { (Test-Path "$HOME\.codex") -or (Has codex) }
        'opencode' { (Test-Path "$HOME\.config\opencode") -or (Has opencode) }
        'cursor' { (Test-Path "$HOME\.cursor") -or (Has cursor) }
        'antigravity' { Test-Path "$HOME\.gemini\antigravity" }
    }
}

$List = @($Agents | ForEach-Object { $_ -split ',' } | Where-Object { $_ })
if ($List -contains 'all') { $List = $AllAgents }
elseif ($List -contains 'auto') {
    $List = @($AllAgents | Where-Object { AgentFound $_ })
    if (-not $List) { $List = @('claude') }
}

# 1. Dependencies
if (-not $SkillsOnly) {
    Say 'Checking tools'
    $missing = $false
    foreach ($t in 'git', 'node', 'npm', 'ffmpeg', 'ffprobe') {
        if (Has $t) { Ok $t } else { Warn "$t not found"; $missing = $true }
    }
    if ($missing) {
        Write-Host '   Install the missing tools, open a new terminal, then run this again:'
        Write-Host '     winget install Git.Git OpenJS.NodeJS.LTS Gyan.FFmpeg'
        exit 1
    }

    Say "OpenMontage: $OM"
    if (Test-Path (Join-Path $OM 'AGENT_GUIDE.md')) { Ok 'found' } else { Run { git clone --depth 1 $OmUrl $OM } }

    $Vpy = Join-Path $OM '.venv\Scripts\python.exe'
    if (-not (Test-Path $Vpy)) {
        $base = $null; $found = @()
        foreach ($c in @(@('py', '-3.12'), @('py', '-3.11'), @('py', '-3.10'), @('python'), @('python3'))) {
            if (-not (Has $c[0])) { continue }
            $v = PyVer $c
            if (PyOk $v) { $base = $c; break }
            if ($v) { $found += "$($c -join ' ')=$v" }
        }
        if (-not $base) {
            Warn "Python 3.10-3.12 is required (faster-whisper). Found: $(if ($found) { $found -join ', ' } else { 'none' })"
            Write-Host '     winget install Python.Python.3.12'
            exit 1
        }
        Say "Creating $OM\.venv with $($base -join ' ') (Python $(PyVer $base))"
        $exe, $rest = $base
        Run { & $exe @rest -m venv (Join-Path $OM '.venv') }
    }
    if ((Test-Path $Vpy) -and -not (PyOk (PyVer @($Vpy)))) {
        Warn "$OM\.venv uses Python $(PyVer @($Vpy)); faster-whisper needs 3.10-3.12."
        Write-Host '     Recreate it with Python 3.12, or pass -OM <another folder>.'
        exit 1
    }
    Say "Python packages ($Vpy)"
    Run { & $Vpy -m pip install -q -r (Join-Path $Src 'requirements.txt') }

    Say 'HyperFrames'
    if (Has hyperframes) { Ok 'hyperframes' } else { Run { npm i -g hyperframes@0.8 } }
    if (-not $NoHfSkills) {
        try { Run { npx -y hyperframes skills } } catch { Warn 'npx hyperframes skills failed; run it by hand later' }
    }

    if ($OM -ne (Join-Path $HOME 'Projects\OpenMontage')) {
        Warn 'OpenMontage is not in ~\Projects\OpenMontage. Run this once:'
        Write-Host "     setx OPENMONTAGE_DIR `"$OM`""
    }
}

# 2. Skills
$BackupRoot = Join-Path $HOME ".reelsmith-backups\$(Get-Date -Format 'yyyyMMdd-HHmmss')"
function TreeHash($dir) {  # relative path + content hash of every file, __pycache__ ignored
    $root = (Resolve-Path $dir).Path
    Get-ChildItem -Recurse -File $root | Where-Object { $_.FullName -notmatch '[\\/]__pycache__[\\/]|\.pyc$' } |
        Sort-Object FullName | ForEach-Object { $_.FullName.Substring($root.Length) + ':' + (Get-FileHash $_.FullName -Algorithm SHA256).Hash }
}
function InstallSkill($agent, $dir, $s) {
    $from = Join-Path $Src "skills\$s"
    $dst = Join-Path $dir $s
    if (Test-Path $dst) {
        if (-not (Compare-Object @(TreeHash $from) @(TreeHash $dst))) { Ok "$agent/$s is already up to date"; return }
        $bak = Join-Path $BackupRoot "$agent\$s"
        if ($DryRun) { Write-Host "   would $(if ($NoBackup) { 'delete' } else { "move to $bak" }): $dst" }
        elseif ($NoBackup) { Remove-Item -Recurse -Force $dst }
        else {
            New-Item -ItemType Directory -Force (Split-Path $bak) | Out-Null
            Move-Item $dst $bak
            Ok "$agent/$s`: your previous copy was saved to $bak"
        }
    }
    if ($DryRun) { Write-Host "   would copy: skills\$s -> $dst"; return }
    Copy-Item -Recurse $from $dst
}
Say "Installing skills for: $($List -join ', ')"
foreach ($a in $List) {
    $dir = AgentDir $a
    if (-not $dir) { Warn "unknown agent: $a"; continue }
    if (-not $DryRun) { New-Item -ItemType Directory -Force $dir | Out-Null }
    foreach ($s in $Skills) { InstallSkill $a $dir $s }
    Ok "$a  ->  $dir"
}

Say 'Done'
Write-Host '   Open your agent and type: /reelsmith <folder>'
Write-Host '   Tools without skill support read AGENTS.md in this repo.'
