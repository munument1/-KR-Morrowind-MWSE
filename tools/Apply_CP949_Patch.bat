@echo off
setlocal
cd /d "%~dp0"

set "INPUT=Morrowind.exe"
set "BACKUP=Morrowind.exe.cp949-backup"
set "INI=Morrowind.ini"
set "INI_BACKUP=Morrowind.ini.cp949-backup"
set "INI_OVERLAY=Morrowind_Korean_INI.ini"

if not exist "%INPUT%" (
  echo [ERROR] Morrowind.exe was not found next to this BAT file.
  echo Extract the Full ZIP into the Morrowind game folder and run this BAT there.
  pause
  exit /b 1
)

if not exist "%INI%" (
  echo [ERROR] Morrowind.ini was not found next to this BAT file.
  pause
  exit /b 1
)

if not exist "%INI_OVERLAY%" (
  echo [ERROR] %INI_OVERLAY% is missing from the Full package.
  pause
  exit /b 1
)

echo [1/2] Checking Morrowind.exe and applying the CP949 patch if needed...

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop';" ^
  "$inputPath=(Join-Path (Get-Location) 'Morrowind.exe');" ^
  "$backupPath=(Join-Path (Get-Location) 'Morrowind.exe.cp949-backup');" ^
  "$supported=@('8fe33fb11b6a682721e7456af78eefd228e8b60dc7c9f4253f89a361f8a4dfc5','c3585b91741689057c18ff86a1c3381d47278cd1d81443d38ed3b179c2fa1cd8','a87ee7f9239023469d4c031e6dab87648a316ab8c1354e96c2478aca3376167c');" ^
  "$reference='a87ee7f9239023469d4c031e6dab87648a316ab8c1354e96c2478aca3376167c';" ^
  "$referenceOut='bff9c8381d59657e5dfbfc66058745996327b20f4516f63e54ce9c7f726b45fc';" ^
  "$patch=[byte[]](0x55,0x89,0xE5,0x8B,0x4D,0x08,0x0F,0xB7,0x01,0x86,0xC4,0x80,0xFC,0x81,0x72,0x34,0x80,0xFC,0xFD,0x77,0x2F,0x80,0xEC,0x81,0x3C,0x41,0x72,0x28,0x3C,0x5A,0x76,0x14,0x3C,0x61,0x72,0x20,0x3C,0x7A,0x76,0x10,0x3C,0x81,0x72,0x18,0x3C,0xFE,0x77,0x14,0x2C,0x4D,0xEB,0x06,0x2C,0x41,0xEB,0x02,0x2C,0x47,0x50,0x3E,0x8B,0x4D,0x0C,0xE9,0x15,0x00,0x00,0x00,0xE9,0x87,0x00,0x00,0x00);" ^
  "$offset=0x3457C0;" ^
  "$bytes=[IO.File]::ReadAllBytes($inputPath);" ^
  "if($bytes.Length -lt ($offset+$patch.Length)){throw 'Morrowind.exe is unexpectedly small.'};" ^
  "$already=$true; for($i=0;$i -lt $patch.Length;$i++){if($bytes[$offset+$i] -ne $patch[$i]){$already=$false;break}};" ^
  "if($already){Write-Host 'Executable is already CP949-patched.'}else{" ^
  "  $hash=(Get-FileHash -Algorithm SHA256 -LiteralPath $inputPath).Hash.ToLowerInvariant();" ^
  "  if($supported -notcontains $hash){throw ('Unsupported Morrowind.exe SHA-256: '+$hash)};" ^
  "  if(Test-Path -LiteralPath $backupPath){throw 'Executable backup already exists but Morrowind.exe is not CP949-patched. Restore/remove the backup before retrying.'};" ^
  "  Copy-Item -LiteralPath $inputPath -Destination $backupPath -ErrorAction Stop;" ^
  "  [Array]::Copy($patch,0,$bytes,$offset,$patch.Length);" ^
  "  [IO.File]::WriteAllBytes($inputPath,$bytes);" ^
  "  $outHash=(Get-FileHash -Algorithm SHA256 -LiteralPath $inputPath).Hash.ToLowerInvariant();" ^
  "  if($hash -eq $reference -and $outHash -ne $referenceOut){Copy-Item -LiteralPath $backupPath -Destination $inputPath -Force; throw ('Output verification failed: '+$outHash)};" ^
  "  Write-Host ('Input SHA-256 : '+$hash); Write-Host ('Output SHA-256: '+$outHash); Write-Host ('Backup         : '+$backupPath);" ^
  "}"

if errorlevel 1 (
  echo.
  echo [FAILED] Morrowind.exe CP949 patch failed.
  pause
  exit /b 1
)

echo.
echo [2/2] Installing 63 Korean display strings into Morrowind.ini...

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop';" ^
  "$enc=[Text.Encoding]::GetEncoding(949);" ^
  "$iniPath=(Join-Path (Get-Location) 'Morrowind.ini');" ^
  "$backupPath=(Join-Path (Get-Location) 'Morrowind.ini.cp949-backup');" ^
  "$overlayPath=(Join-Path (Get-Location) 'Morrowind_Korean_INI.ini');" ^
  "if(!(Test-Path -LiteralPath $backupPath)){Copy-Item -LiteralPath $iniPath -Destination $backupPath -ErrorAction Stop};" ^
  "$map=@{}; $section=$null; $overlay=[IO.File]::ReadAllLines($overlayPath,$enc);" ^
  "foreach($line in $overlay){if($line -match '^\[(.+)\]$'){$section=$Matches[1];if(!$map.ContainsKey($section)){$map[$section]=@{}};continue};if([string]::IsNullOrWhiteSpace($line)){continue};$eq=$line.IndexOf('=');if($section -and $eq -gt 0){$map[$section][$line.Substring(0,$eq)]=$line.Substring($eq+1)}};" ^
  "$entryCount=0; foreach($s in $map.Keys){$entryCount+=$map[$s].Count}; if($entryCount -ne 63){throw ('Unexpected INI overlay entry count: '+$entryCount)};" ^
  "$src=[IO.File]::ReadAllLines($iniPath,$enc); $out=New-Object System.Collections.Generic.List[string]; $seen=@{}; $done=@{}; $current=$null;" ^
  "foreach($line in $src){" ^
  "  if($line -match '^\[(.+)\]\s*$'){" ^
  "    if($current -and $map.ContainsKey($current)){foreach($k in $map[$current].Keys){$id=$current+[char]0+$k;if(!$done.ContainsKey($id)){$out.Add($k+'='+$map[$current][$k]);$done[$id]=$true}}};" ^
  "    $current=$Matches[1]; $seen[$current]=$true; $out.Add($line); continue" ^
  "  };" ^
  "  if($current -and $map.ContainsKey($current)){" ^
  "    $eq=$line.IndexOf('='); if($eq -gt 0){$key=$line.Substring(0,$eq).Trim(); if($map[$current].ContainsKey($key)){$out.Add($key+'='+$map[$current][$key]);$done[$current+[char]0+$key]=$true;continue}}" ^
  "  };" ^
  "  $out.Add($line)" ^
  "};" ^
  "if($current -and $map.ContainsKey($current)){foreach($k in $map[$current].Keys){$id=$current+[char]0+$k;if(!$done.ContainsKey($id)){$out.Add($k+'='+$map[$current][$k]);$done[$id]=$true}}};" ^
  "foreach($s in $map.Keys){if(!$seen.ContainsKey($s)){if($out.Count -gt 0 -and $out[$out.Count-1] -ne ''){$out.Add('')};$out.Add('['+$s+']');foreach($k in $map[$s].Keys){$out.Add($k+'='+$map[$s][$k]);$done[$s+[char]0+$k]=$true}}};" ^
  "[IO.File]::WriteAllLines($iniPath,$out,$enc);" ^
  "$actual=@{}; $section=$null; foreach($line in [IO.File]::ReadAllLines($iniPath,$enc)){if($line -match '^\[(.+)\]\s*$'){$section=$Matches[1];if(!$actual.ContainsKey($section)){$actual[$section]=@{}};continue};$eq=$line.IndexOf('=');if($section -and $eq -gt 0){$actual[$section][$line.Substring(0,$eq).Trim()]=$line.Substring($eq+1)}};" ^
  "foreach($s in $map.Keys){if(!$actual.ContainsKey($s)){throw ('Missing section after write: ['+$s+']')};foreach($k in $map[$s].Keys){if(!$actual[$s].ContainsKey($k) -or $actual[$s][$k] -ne $map[$s][$k]){throw ('INI value verification failed: ['+$s+'] '+$k)}}};" ^
  "Write-Host ('Morrowind.ini backup: '+$backupPath); Write-Host 'Installed: 40 class-question strings + 20 level-up strings + 3 blood display names.'"

if errorlevel 1 (
  echo.
  echo [FAILED] Morrowind.ini Korean display-string patch failed.
  pause
  exit /b 1
)

echo.
echo [OK] CP949 executable and Korean Classic INI display strings are installed.
echo Enable Morrowind_Korean_ReTranslation.esp in the launcher.
echo.
pause
exit /b 0
