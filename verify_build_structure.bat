@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Streamlit Build Structure Verification
echo ============================================
echo.

set "BUILD_DIR=dist\logistics_app"
set "INTERNAL_DIR=%BUILD_DIR%\_internal"

if not exist "%BUILD_DIR%" (
  echo [ERROR] Build directory not found: %BUILD_DIR%
  echo Please run the build script first.
  pause
  exit /b 1
)

echo [1] Checking main executable...
if exist "%BUILD_DIR%\logistics_app.exe" (
  echo [OK] logistics_app.exe found
) else (
  echo [ERROR] logistics_app.exe NOT found
)
echo.

echo [2] Checking _internal directory...
if exist "%INTERNAL_DIR%" (
  echo [OK] _internal directory found
) else (
  echo [ERROR] _internal directory NOT found
  pause
  exit /b 1
)
echo.

echo [3] Checking Streamlit package structure...
if exist "%INTERNAL_DIR%\streamlit" (
  echo [OK] streamlit directory found
) else (
  echo [ERROR] streamlit directory NOT found
  pause
  exit /b 1
)
echo.

echo [4] Checking critical Streamlit static files...
if exist "%INTERNAL_DIR%\streamlit\static" (
  echo [OK] streamlit\static directory found
  if exist "%INTERNAL_DIR%\streamlit\static\index.html" (
    echo [OK] index.html found
  ) else (
    echo [ERROR] index.html NOT found
  )
) else (
  echo [ERROR] streamlit\static directory NOT found
)
echo.

echo [5] Checking Streamlit templates...
if exist "%INTERNAL_DIR%\streamlit\web\server\templates" (
  echo [OK] templates directory found
) else (
  echo [ERROR] templates directory NOT found
)
echo.

echo [6] Listing streamlit\static contents:
if exist "%INTERNAL_DIR%\streamlit\static" (
  dir /B "%INTERNAL_DIR%\streamlit\static"
) else (
  echo [SKIP] Directory not found
)
echo.

echo [7] Checking for alternative locations...
if exist "%INTERNAL_DIR%\streamlit-1.51.0.dist-info" (
  echo [INFO] Found streamlit-1.51.0.dist-info
)
if exist "%INTERNAL_DIR%\streamlit.libs" (
  echo [INFO] Found streamlit.libs
)
echo.

echo [8] Searching for index.html in _internal...
dir /S /B "%INTERNAL_DIR%\*index.html" 2>nul
if errorlevel 1 (
  echo [WARNING] No index.html found anywhere in _internal
) else (
  echo [INFO] Found index.html files above
)
echo.

echo [9] Directory tree of streamlit folder:
if exist "%INTERNAL_DIR%\streamlit" (
  tree /F "%INTERNAL_DIR%\streamlit" | findstr /V /C:"├" /C:"│" /C:"└" /C:"─"
) else (
  echo [SKIP] streamlit directory not found
)
echo.

echo ============================================
echo   Verification Complete
echo ============================================
pause