@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Fix Streamlit Static Files
echo ============================================
echo.

set "VENV_PY=venv\Scripts\python.exe"
set "BUILD_DIR=dist\logistics_app"
set "INTERNAL_DIR=%BUILD_DIR%\_internal"

REM Get Streamlit package directory
set "TMP_FILE=_temp_streamlit_path.txt"
"%VENV_PY%" -c "import streamlit, os; print(os.path.dirname(streamlit.__file__))" > "%TMP_FILE%" 2>&1
set /p STREAMLIT_DIR=<"%TMP_FILE%"
del "%TMP_FILE%" 2>nul

if not defined STREAMLIT_DIR (
  echo [ERROR] Could not find Streamlit package directory
  pause
  exit /b 1
)

echo [INFO] Streamlit package: %STREAMLIT_DIR%
echo [INFO] Target directory: %INTERNAL_DIR%
echo.

if not exist "%INTERNAL_DIR%" (
  echo [ERROR] _internal directory not found. Build the app first.
  pause
  exit /b 1
)

echo [STEP 1] Creating streamlit directory structure...
if not exist "%INTERNAL_DIR%\streamlit" mkdir "%INTERNAL_DIR%\streamlit"
if not exist "%INTERNAL_DIR%\streamlit\web" mkdir "%INTERNAL_DIR%\streamlit\web"
if not exist "%INTERNAL_DIR%\streamlit\web\server" mkdir "%INTERNAL_DIR%\streamlit\web\server"
echo [OK]
echo.

echo [STEP 2] Copying static files...
if exist "%STREAMLIT_DIR%\static" (
  rmdir /S /Q "%INTERNAL_DIR%\streamlit\static" 2>nul
  xcopy /E /I /Y /Q "%STREAMLIT_DIR%\static" "%INTERNAL_DIR%\streamlit\static"
  if errorlevel 1 (
    echo [ERROR] Failed to copy static files
    pause
    exit /b 1
  )
  echo [OK] Static files copied
) else (
  echo [ERROR] Source static directory not found: %STREAMLIT_DIR%\static
  pause
  exit /b 1
)
echo.

echo [STEP 3] Copying template files...
if exist "%STREAMLIT_DIR%\web\server\templates" (
  rmdir /S /Q "%INTERNAL_DIR%\streamlit\web\server\templates" 2>nul
  xcopy /E /I /Y /Q "%STREAMLIT_DIR%\web\server\templates" "%INTERNAL_DIR%\streamlit\web\server\templates"
  if errorlevel 1 (
    echo [ERROR] Failed to copy template files
    pause
    exit /b 1
  )
  echo [OK] Template files copied
) else (
  echo [ERROR] Source templates directory not found: %STREAMLIT_DIR%\web\server\templates
  pause
  exit /b 1
)
echo.

echo [STEP 4] Verifying critical files...
if exist "%INTERNAL_DIR%\streamlit\static\index.html" (
  echo [OK] index.html found
) else (
  echo [ERROR] index.html still missing!
  echo.
  echo Checking what's in static folder:
  dir /B "%INTERNAL_DIR%\streamlit\static"
  pause
  exit /b 1
)
echo.

echo [STEP 5] Listing copied structure...
echo Static files:
dir /B "%INTERNAL_DIR%\streamlit\static"
echo.
echo Template files:
dir /B "%INTERNAL_DIR%\streamlit\web\server\templates"
echo.

echo ============================================
echo   Fix Complete!
echo ============================================
echo.
echo You can now run: %BUILD_DIR%\run_logistics_app.bat
echo.
pause