REM You can run this in an (https://sandboxie-plus.com/) to clear the unnecesary extentions from the sandboxed Firefox
REM for /f %%x in ('dir /s /b /o:gn "%appdata%\Mozilla\Firefox\Profiles" ^| findstr /v /i "lastpass" ^| findstr .xpi') do DEL %%x
cd %appdata%\Mozilla\Firefox\Profiles
for /f %%f in ('dir /b /o:gn "%appdata%\Mozilla\Firefox\Profiles\*"') do for /f %%g in ('dir /b %%f\extensions\*.xpi ^| findstr /v /i "lastpass"') do del %%g
"C:\Program Files\Mozilla Firefox\firefox.exe"
