@echo off
REM Job Hunter - Resume Encoder (Windows)
REM Usage: encode_resume.bat resume.pdf
REM Encodes your resume to base64 and saves to file or clipboard

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Usage: %0 ^<resume.pdf^>
    echo.
    echo Encodes your resume to base64 and saves it to a file.
    echo Paste the result into GitHub Settings ^> Secrets ^> RESUME_B64
    echo.
    echo Examples:
    echo   %0 resume.pdf
    echo   %0 "My Resume.docx"
    exit /b 1
)

set "FILE=%~1"

REM Check if file exists
if not exist "%FILE%" (
    echo ❌ Error: File not found: %FILE%
    exit /b 1
)

REM Get file size for display
for %%A in ("%FILE%") do set "FILE_SIZE=%%~zA"

echo 🔄 Encoding %FILE% to base64...

REM Use certutil to encode (built-in Windows utility)
REM First, copy to temp, encode, then read
setlocal enabledelayedexpansion

set "TEMP_INPUT=%TEMP%\job_hunter_resume.tmp"
set "TEMP_OUTPUT=%TEMP%\job_hunter_resume_b64.tmp"

copy "%FILE%" "!TEMP_INPUT!" >nul

REM Use PowerShell for more reliable base64 encoding
powershell -Command "[Convert]::ToBase64String([IO.File]::ReadAllBytes('%FILE%')) | Out-File -FilePath '%TEMP_OUTPUT%' -Encoding ASCII"

if not exist "%TEMP_OUTPUT%" (
    echo ❌ Error: Failed to encode file
    exit /b 1
)

REM Copy output file to current directory
set "OUTPUT_FILE=resume_b64.txt"
copy "%TEMP_OUTPUT%" "%OUTPUT_FILE%" >nul

REM Clean up temp files
del "%TEMP_INPUT%" "%TEMP_OUTPUT%" 2>nul

echo.
echo 📊 Summary:
echo    File: %FILE%
echo    Size: %FILE_SIZE% bytes
echo    Output: %OUTPUT_FILE%
echo.
echo 📋 Next steps:
echo 1. Open resume_b64.txt
echo 2. Copy the entire contents
echo 3. Go to your GitHub repository
echo 4. Settings ^> Secrets and variables ^> Actions
echo 5. Click 'New repository secret'
echo 6. Name: RESUME_B64
echo 7. Paste the base64 string
echo 8. Click 'Add secret'
echo.
echo ✨ Done! Your resume is encoded and ready to use in GitHub Actions.
echo.
echo The base64 string has been saved to: %OUTPUT_FILE%
pause
