@echo off
setlocal
echo Uninstalling MayleSoft...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$d='C:\Users\kamaa\dev\ngo_fundraising'; $s='C:\Users\kamaa\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\MayleSoft'; $desktop=[Environment]::GetFolderPath('Desktop'); Remove-Item -LiteralPath $s -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -LiteralPath (Join-Path $desktop 'MayleSoft.lnk') -Force -ErrorAction SilentlyContinue; Start-Process cmd.exe -ArgumentList ('/c timeout /t 2 /nobreak >nul & rmdir /s /q "' + $d + '"') -WindowStyle Hidden"
