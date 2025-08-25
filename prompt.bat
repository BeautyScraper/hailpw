REM @echo off
:: Check if the user provided a file name
if "%1"=="" (
    echo Usage: %~nx0 filename
    exit /b
)

:: Set the target directory
set targetDir=C:\Personal\Developed\Hailuio\files

:: Create the directory if it doesn't exist
if not exist "%targetDir%" (
    mkdir "%targetDir%"
)

:: Create the text file
REM echo.>"%targetDir%\%1.txt"

:: Open the file in VS Code
code "%targetDir%\%1.txt"
