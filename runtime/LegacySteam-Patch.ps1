param([string]$Mode = 'Install')
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$pack = Join-Path $root 'LegacySteam'
$backup = Join-Path $root 'LegacySteam-Backup'
$previousBackup = Join-Path $root 'LegacySteam-Test1-Backup'
$stage = $null
$success = $false
function FileHash([string]$Path) {
 $sha = [Security.Cryptography.SHA256]::Create()
 $stream = [IO.File]::OpenRead($Path)
 try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','').ToLowerInvariant() }
 finally { $stream.Close(); $sha.Clear() }
}
function OriginalSource($Target) {
 $saved = Join-Path $backup $Target.Path
 if ((Test-Path $saved) -and (FileHash $saved) -eq $Target.Original) { return $saved }
 $saved = Join-Path $previousBackup $Target.Path
 if ((Test-Path $saved) -and (FileHash $saved) -eq $Target.Original) { return $saved }
 $current = Join-Path $root $Target.Path
 if ((Test-Path $current) -and (FileHash $current) -eq $Target.Original) { return $current }
 throw ('Original file or valid backup missing: ' + $Target.Path)
}
Start-Transcript -Path (Join-Path $root 'tML-LegacySteam-Install.txt') -Force
try {
 if ($Mode -ne 'Install' -and $Mode -ne 'Restore') { throw 'Invalid mode.' }
 if ([IntPtr]::Size -ne 8) { throw 'Use the supplied 64-bit BAT launcher.' }
 . (Join-Path $pack 'manifest.ps1')
 Add-Type -Path (Join-Path $pack 'GameFingerprint.cs')
 $gameTarget = $LegacySteamTargets | Where-Object { $_.Path -eq 'tModLoader.dll' }
 $gameCurrent = Join-Path $root 'tModLoader.dll'
 $gameSaved = Join-Path $backup 'tModLoader.dll'
 $statePath = Join-Path $backup 'GameFingerprint-state.txt'
 $dynamicGame = $null
 if (Test-Path $statePath) {
  $state = @(Get-Content -LiteralPath $statePath)
  if ($state.Count -ne 2 -or $state[0] -notmatch '^[0-9a-f]{64}$' -or $state[1] -notmatch '^[0-9a-f]{64}$') { throw 'Invalid game backup state.' }
  if (!(Test-Path $gameSaved) -or (FileHash $gameSaved) -ne $state[0]) { throw 'Game backup is missing or damaged.' }
  $gameTarget.Original = $state[0]; $gameTarget.Patched = $state[1]
 }
 if ((Test-Path $gameCurrent) -and (FileHash $gameCurrent) -ne $gameTarget.Patched) {
  $dynamicGame = [LegacyGameFingerprint]::Apply([IO.File]::ReadAllBytes($gameCurrent),'3bae3a5ecad22eec751e154f68e09361','4b27c35644619f18f97459aa122ec3e1')
  $gameTarget.Original = FileHash $gameCurrent
  $sha = [Security.Cryptography.SHA256]::Create()
  try { $gameTarget.Patched = ([BitConverter]::ToString($sha.ComputeHash($dynamicGame))).Replace('-','').ToLowerInvariant() } finally { $sha.Clear() }
  if ((Test-Path $gameSaved) -and (FileHash $gameSaved) -ne $gameTarget.Original) { throw 'Game version changed since backup. Preserve the old backup, then move LegacySteam-Backup outside the game folder and retry.' }
 }
 elseif ((Test-Path $gameCurrent) -and (FileHash $gameCurrent) -eq $gameTarget.Patched) {
  $source = OriginalSource $gameTarget
  $dynamicGame = [LegacyGameFingerprint]::Apply([IO.File]::ReadAllBytes($source),'3bae3a5ecad22eec751e154f68e09361','4b27c35644619f18f97459aa122ec3e1')
  $sha = [Security.Cryptography.SHA256]::Create()
  try { $verified = ([BitConverter]::ToString($sha.ComputeHash($dynamicGame))).Replace('-','').ToLowerInvariant() } finally { $sha.Clear() }
  if ($verified -ne $gameTarget.Patched) { throw 'Game fingerprint state does not match regenerated output.' }
 }
 $active = @(Get-WmiObject Win32_Process -Filter "Name='dotnet.exe'" | Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($root,[StringComparison]::OrdinalIgnoreCase) })
 if ($active.Count -gt 0) { throw 'Close tModLoader first.' }
 $already = $true
 foreach ($t in $LegacySteamTargets) {
  $current = Join-Path $root $t.Path
  if (!(Test-Path $current)) { throw ('Target missing: ' + $t.Path) }
  $hash = FileHash $current
  if ($hash -ne $t.Original -and $hash -ne $t.Patched) { throw ('Unsupported or updated file. Nothing replaced: ' + $t.Path) }
  if ($hash -ne $t.Patched) { $already = $false }
  $null = OriginalSource $t
 }
 if ($Mode -eq 'Restore') {
  foreach ($t in $LegacySteamTargets) {
   $original = OriginalSource $t
   $destination = Join-Path $root $t.Path
   if ($original -ne $destination) { Copy-Item -LiteralPath $original -Destination $destination -Force }
   if ((FileHash $destination) -ne $t.Original) { throw ('Restore verification failed: ' + $t.Path) }
  }
  Write-Output 'RESTORED: original game and Steamworks files.'
  $success = $true
 } elseif ($already) {
  Write-Output ('Already installed: ' + $LegacySteamVersion)
  $success = $true
 } else {
  foreach ($t in $LegacySteamTargets) {
   $patch = Join-Path $pack $t.PatchFile
   if (!(Test-Path $patch) -or (FileHash $patch) -ne $t.PatchHash) { throw ('Missing or damaged patch: ' + $t.Path) }
  }
  $ps = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
  & $ps -NoProfile -ExecutionPolicy Bypass -File (Join-Path $pack 'Check-Legacy.ps1') -Root $root
  if ($LASTEXITCODE -ne 0) { throw 'Legacy interface preflight failed. No DLLs replaced. Send tML-LegacySteam-Check.txt.' }
  Add-Type -Path (Join-Path $pack 'DeltaPatch.cs')
  $stage = Join-Path $root ('.LegacySteam-stage-' + [Guid]::NewGuid().ToString('N'))
  New-Item -ItemType Directory -Path $stage | Out-Null
  # Produce and verify every output before replacing any game file.
  foreach ($t in $LegacySteamTargets) {
   $original = OriginalSource $t
   $saved = Join-Path $backup $t.Path
   if (Test-Path $saved) {
    if ((FileHash $saved) -ne $t.Original) { throw ('Invalid existing backup: ' + $t.Path) }
   } else {
    New-Item -ItemType Directory -Path (Split-Path $saved) -Force | Out-Null
    Copy-Item -LiteralPath $original -Destination $saved
   }
   if ($t.Path -eq 'tModLoader.dll') { $result = $dynamicGame } else { $result = [LegacyDeltaPatch]::Apply([IO.File]::ReadAllBytes($saved),[IO.File]::ReadAllBytes((Join-Path $pack $t.PatchFile))) }
   $destination = Join-Path $stage $t.Path
   New-Item -ItemType Directory -Path (Split-Path $destination) -Force | Out-Null
   [IO.File]::WriteAllBytes($destination,$result)
   if ((FileHash $destination) -ne $t.Patched) { throw ('Patched output verification failed: ' + $t.Path) }
  }
  [IO.File]::WriteAllLines($statePath,[string[]]@($gameTarget.Original,$gameTarget.Patched))
  try {
   foreach ($t in $LegacySteamTargets) {
    Copy-Item -LiteralPath (Join-Path $stage $t.Path) -Destination (Join-Path $root $t.Path) -Force
    if ((FileHash (Join-Path $root $t.Path)) -ne $t.Patched) { throw ('Write verification failed: ' + $t.Path) }
   }
  } catch {
   $failure = $_
   foreach ($t in $LegacySteamTargets) { Copy-Item -LiteralPath (Join-Path $backup $t.Path) -Destination (Join-Path $root $t.Path) -Force }
   throw $failure
  }
  Write-Output ('INSTALLED: ' + $LegacySteamVersion + '. Start tModLoader normally.')
  Write-Output 'Keep LegacySteam-Backup. Restore-LegacySteam.bat reverses this patch.'
  $success = $true
 }
} catch { Write-Output ('ERROR: ' + $_.Exception.Message) }
finally {
 if ($stage -and (Test-Path $stage)) { Remove-Item -LiteralPath $stage -Recurse -Force }
 Stop-Transcript
}
if ($success) { exit 0 } else { exit 1 }
