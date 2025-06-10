@echo off
setlocal enabledelayedexpansion

:: Loop through all .zip files
for %%f in (*.zip) do (
    echo Unzipping %%f...
    powershell -nologo -noprofile -command ^
        "Expand-Archive -LiteralPath '%%~dpnxf' -DestinationPath "%cd%" -Force"
    
    echo Deleting %%f...
    del "%%f"
)

echo All ZIP files extracted and deleted.
