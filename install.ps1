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
#   -DryRun        show what would happen, change nothing
param(
    [string[]]$Agents = @('auto'),
    [switch]$Project,
    [string]$OM = $(if ($env:OPENMONTAGE_DIR) { $env:OPENMONTAGE_DIR } else { Join-Path $HOME 'Projects\OpenMontage' }),
    [switch]$SkillsOnly,
    [switch]$NoHfSkills,
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
function Run([scriptblock]$b) {
    if ($DryRun) { Write-Host "   would run: $b" } else { & $b; if ($LASTEXITCODE) { throw "failed: $b" } }
}

# Repo source: the folder this script is in, or a fresh clone when run from the web.
$Src = $PSScriptRoot
if (-not $Src -or -not (Test-Path (Join-Path $Src 'skills\reelsmith\SKILL.md'))) {
    $Src = if ($env:REELSMITH_HOME) { $env:REELSMITH_HOME } else { Join-Path $HOME '.reelsmith' }
    Say "Getting Reelsmith into $Src"
    if (Test-Path (Join-Path $Src '.git')) { Run { git -C $Src pull --ff-only } }
    else { Run { git clone --depth 1 $RepoUrl $Src } }
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
        # faster-whisper needs Python 3.10 - 3.12
        Say "Creating $OM\.venv"
        $has312 = $false
        if (Has py) { try { $has312 = [bool](& py -3.12 --version 2>$null) } catch {} }
        if ($has312) { Run { py -3.12 -m venv (Join-Path $OM '.venv') } }
        elseif (Has python) { Warn 'py -3.12 not found, using "python". faster-whisper needs Python 3.10 - 3.12.'; Run { python -m venv (Join-Path $OM '.venv') } }
        else { Warn 'Python 3.12 not found. Install it: winget install Python.Python.3.12'; exit 1 }
    }
    Say "Python packages ($Vpy)"
    Run { & $Vpy -m pip install -q -r (Join-Path $Src 'requirements.txt') }

    Say 'HyperFrames'
    if (Has hyperframes) { Ok 'hyperframes' } else { Run { npm i -g hyperframes } }
    if (-not $NoHfSkills) {
        try { Run { npx -y hyperframes skills } } catch { Warn 'npx hyperframes skills failed; run it by hand later' }
    }

    if ($OM -ne (Join-Path $HOME 'Projects\OpenMontage')) {
        Warn 'OpenMontage is not in ~\Projects\OpenMontage. Run this once:'
        Write-Host "     setx OPENMONTAGE_DIR `"$OM`""
    }
}

# 2. Skills
Say "Installing skills for: $($List -join ', ')"
foreach ($a in $List) {
    $dir = AgentDir $a
    if (-not $dir) { Warn "unknown agent: $a"; continue }
    foreach ($s in $Skills) {
        $dst = Join-Path $dir $s
        if ($DryRun) { Write-Host "   would copy: skills\$s -> $dst"; continue }
        New-Item -ItemType Directory -Force $dir | Out-Null
        if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
        Copy-Item -Recurse (Join-Path $Src "skills\$s") $dst
    }
    Ok "$a  ->  $dir"
}

Say 'Done'
Write-Host '   Open your agent and type: /reelsmith <folder>'
Write-Host '   Tools without skill support read AGENTS.md in this repo.'
