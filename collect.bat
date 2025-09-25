set /p dirname=Enter the name of the directory to create: 

:: Check if the directory already exists

cd C:\Personal\Developed\Hailuio\gemni_downloads
ren * *.png
REM double_d.py %cd%


if exist "%dirname%" (
    echo Directory "%dirname%" already exists.
) else (
    mkdir "%dirname%"
    echo Directory "%dirname%" created successfully.
)


move *.png "%dirname%"
move *.txt "%dirname%"