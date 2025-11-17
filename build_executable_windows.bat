@echo on
setlocal enableextensions enabledelayedexpansion

REM ===================== SAFE START =====================
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM ===================== CONFIG =====================
set "VENV_DIR=%SCRIPT_DIR%venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "LOG=%SCRIPT_DIR%build_full.log"
set "BUILD_NAME=logistics_app"
REM onedir for debug, onefile for single-EXE packaging
set "BUILD_MODE=onedir"
set "HEARTBEAT_SECS=15"
set "HOOK_DIR=%SCRIPT_DIR%pyi_hooks"
set "USE_FIX_METADATA_HOOK_ONEFILE=0"
set "PYTHONUTF8=1"

REM ================== PREP & LOGGING =================
del "%LOG%" 2>nul
echo === BUILD START: %DATE% %TIME% ===>>"%LOG%"

echo [INFO] Host Pythons on PATH:>>"%LOG%"
where python >>"%LOG%" 2>&1

if not exist "%VENV_DIR%" (
  echo [TIME] Create venv start: %DATE% %TIME%>>"%LOG%"
  python -m venv "%VENV_DIR%" >>"%LOG%" 2>&1 || (echo [ERROR] venv create failed & goto :showlog_err)
  echo [TIME] Create venv end:   %DATE% %TIME%>>"%LOG%"
)

echo [INFO] Using interpreter: "%VENV_PY%">>"%LOG%"
"%VENV_PY%" --version>>"%LOG%" 2>&1
"%VENV_PY%" -m pip --version>>"%LOG%" 2>&1

REM =================== DEPENDENCIES ==================
echo [TIME] pip upgrade start: %DATE% %TIME%>>"%LOG%"
"%VENV_PY%" -m pip install --upgrade pip >>"%LOG%" 2>&1 || goto :showlog_err
echo [TIME] pip upgrade end:   %DATE% %TIME%>>"%LOG%"

echo [TIME] deps install start: %DATE% %TIME%>>"%LOG%"
"%VENV_PY%" -m pip install -r "%SCRIPT_DIR%requirements.txt" >>"%LOG%" 2>&1 || goto :showlog_err
"%VENV_PY%" -m pip install --upgrade pyinstaller >>"%LOG%" 2>&1 || goto :showlog_err
"%VENV_PY%" -m pip install validators >>"%LOG%" 2>&1
echo [TIME] deps install end:   %DATE% %TIME%>>"%LOG%"

echo [INFO] Frozen deps (pip freeze):>>"%LOG%"
"%VENV_PY%" -m pip freeze >>"%LOG%" 2>&1

REM ============== PREFLIGHT METADATA CHECK ===========
for /F "usebackq delims=" %%V in (`"%VENV_PY%" -c "import importlib.metadata as m; print(m.version('streamlit'))"`) do set "STREAMLIT_VER=%%V"
if not defined STREAMLIT_VER set "STREAMLIT_VER=1.51.0"
set "STREAMLIT_BUNDLED_VERSION=%STREAMLIT_VER%"
echo [INFO] STREAMLIT_BUNDLED_VERSION=%STREAMLIT_BUNDLED_VERSION%>>"%LOG%"

REM *** ROBUST: capture the actual Streamlit package dir to a temp file, then read it ***
set "TMP_SL_FILE=%SCRIPT_DIR%_streamlit_dir.txt"
del "%TMP_SL_FILE%" 2>nul
"%VENV_PY%" - <<#PY 1>"%TMP_SL_FILE%" 2>>"%LOG%"
import streamlit, os, sys
sys.stdout.write(os.path.dirname(streamlit.__file__))
#PY
set /p STREAMLIT_PKG_DIR=<"%TMP_SL_FILE%"
del "%TMP_SL_FILE%" 2>nul

if not defined STREAMLIT_PKG_DIR (
  REM Fallback guess
  set "STREAMLIT_PKG_DIR=%VENV_DIR%\Lib\site-packages\streamlit"
)

echo [INFO] STREAMLIT_PKG_DIR=%STREAMLIT_PKG_DIR%>>"%LOG%"
if not exist "%STREAMLIT_PKG_DIR%\__init__.py" (
  echo [ERROR] STREAMLIT_PKG_DIR not valid: "%STREAMLIT_PKG_DIR%">>"%LOG%"
  goto :showlog_err
)

REM ================== CLEAN ARTIFACTS =================
echo [TIME] clean start: %DATE% %TIME%>>"%LOG%"
if exist "%SCRIPT_DIR%build" rmdir /S /Q "%SCRIPT_DIR%build" >>"%LOG%" 2>&1
if exist "%SCRIPT_DIR%dist"  rmdir /S /Q "%SCRIPT_DIR%dist"  >>"%LOG%" 2>&1
del /Q "%SCRIPT_DIR%*.spec"  >>"%LOG%" 2>&1
echo [TIME] clean end:   %DATE% %TIME%>>"%LOG%"

REM ============= SANITY CHECK: STREAMLIT =============
"%VENV_PY%" -c "import sys, streamlit; print('PY=',sys.executable); print('STREAMLIT=',streamlit.__file__)" >>"%LOG%" 2>&1 || goto :showlog_err

REM ================== HOOKS GUARD ====================
if not exist "%HOOK_DIR%\rth_streamlit_version_shim.py" (
  echo [ERROR] Missing hook: "%HOOK_DIR%\rth_streamlit_version_shim.py">>"%LOG%"
  echo [ERROR] Create pyi_hooks\rth_streamlit_version_shim.py and re-run.>>"%LOG%"
  goto :showlog_err
)

REM ================== START LIVE TAIL =================
start "TAIL_LOG" powershell -NoProfile -Command "Get-Content -Path '%LOG%' -Wait"

REM ================== START HEARTBEAT =================
start "HB_LOG" powershell -NoProfile -Command ^
  "$p='%SCRIPT_DIR%'; $log=Join-Path $p 'build_full.log'; $b=Join-Path $p 'build'; while($true){ if(Test-Path $b){ $s=(Get-ChildItem -Recurse -File $b -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum; $mb=[math]::Round(($s/1MB),2); Add-Content -Path $log -Value ('[HB] {0} build size: {1} MB' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $mb) } else { Add-Content -Path $log -Value ('[HB] {0} build folder not present yet' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')) }; Start-Sleep %HEARTBEAT_SECS% }"

REM ===================== BUILD =======================
echo [TIME] build start: %DATE% %TIME%>>"%LOG%"

REM keep console ON for diagnostics
set "COMMON_PYI_FLAGS=--noconfirm --clean --log-level=INFO --name %BUILD_NAME% --additional-hooks-dir ""%HOOK_DIR%"""

set "DATA_FLAGS=^
 --add-data ""Overview.py;."" ^
 --add-data ""pages;pages"" ^
 --add-data ""utils;utils"" ^
 --add-data "".streamlit;.streamlit"" ^
 --add-data ""DB;DB"" ^
 --add-data ""logo.svg;."" ^
 --add-data "".env;."" ""

REM CRITICAL: explicitly bundle Streamlit static & templates
set "STREAMLIT_DATA_FLAGS=^
 --add-data ""%STREAMLIT_PKG_DIR%\static;streamlit\static"" ^
 --add-data ""%STREAMLIT_PKG_DIR%\web\server\templates;streamlit\web\server\templates"" "

set "HIDDEN_FLAGS=^
 --hidden-import=streamlit.web.cli ^
 --hidden-import=openpyxl.utils.dataframe ^
 --hidden-import=dotenv"

set "COLLECT_FLAGS=^
 --collect-all streamlit ^
 --collect-data streamlit ^
 --collect-data streamlit.web ^
 --collect-all pyarrow ^
 --collect-all protobuf ^
 --collect-all tornado ^
 --collect-all watchdog ^
 --collect-submodules pandas ^
 --collect-submodules numpy ^
 --copy-metadata streamlit ^
 --copy-metadata click ^
 --copy-metadata altair ^
 --copy-metadata validators ^
 --collect-metadata streamlit ^
 --collect-metadata click ^
 --collect-metadata altair"

set "EXCLUDE_FLAGS=^
 --exclude-module streamlit.external.langchain ^
 --exclude-module tests ^
 --exclude-module pytest"

if /I "%BUILD_MODE%"=="onedir" (
  "%VENV_PY%" -m PyInstaller ^
    %COMMON_PYI_FLAGS% ^
    --onedir ^
    %DATA_FLAGS% ^
    %STREAMLIT_DATA_FLAGS% ^
    %HIDDEN_FLAGS% ^
    %COLLECT_FLAGS% ^
    %EXCLUDE_FLAGS% ^
    "%SCRIPT_DIR%run_streamlit_bootstrap.py" >>"%LOG%" 2>&1
) else (
  "%VENV_PY%" -m PyInstaller ^
    %COMMON_PYI_FLAGS% ^
    --onefile ^
    %DATA_FLAGS% ^
    %STREAMLIT_DATA_FLAGS% ^
    %HIDDEN_FLAGS% ^
    %COLLECT_FLAGS% ^
    %EXCLUDE_FLAGS% ^
    "%SCRIPT_DIR%run_streamlit_bootstrap.py" >>"%LOG%" 2>&1
)

set "BUILD_RC=%ERRORLEVEL%"
echo [TIME] build end:   %DATE% %TIME%>>"%LOG%"

REM ================== STOP TAIL/HEARTBEAT =============
taskkill /F /FI "WINDOWTITLE eq TAIL_LOG" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq HB_LOG"   >nul 2>&1

if NOT "%BUILD_RC%"=="0" goto :showlog_err

REM ========== POST-BUILD SAFETY COPY OF STATIC =========
set "INTERNAL_DIR=%SCRIPT_DIR%dist\%BUILD_NAME%\_internal"
if exist "%INTERNAL_DIR%" (
  echo [INFO] Post-copy Streamlit static/templates into _internal>>"%LOG%"
  if exist "%STREAMLIT_PKG_DIR%\static" (
    xcopy /E /I /Y "%STREAMLIT_PKG_DIR%\static" "%INTERNAL_DIR%\streamlit\static" >>"%LOG%" 2>&1
  )
  if exist "%STREAMLIT_PKG_DIR%\web\server\templates" (
    xcopy /E /I /Y "%STREAMLIT_PKG_DIR%\web\server\templates" "%INTERNAL_DIR%\streamlit\web\server\templates" >>"%LOG%" 2>&1
  )
)

REM ================ MOVE/COPY ARTIFACTS ===============
mkdir "%SCRIPT_DIR%release" 2>nul
if /I "%BUILD_MODE%"=="onedir" (
  if exist "%SCRIPT_DIR%dist\%BUILD_NAME%" (
    rmdir /S /Q "%SCRIPT_DIR%release\%BUILD_NAME%" 2>nul
    xcopy /E /I /Y "%SCRIPT_DIR%dist\%BUILD_NAME%" "%SCRIPT_DIR%release\%BUILD_NAME%" >>"%LOG%" 2>&1
  ) else (
    echo [ERROR] dist\%BUILD_NAME% not found>>"%LOG%"
    goto :showlog_err
  )
) else (
  if exist "%SCRIPT_DIR%dist\%BUILD_NAME%.exe" (
    move /Y "%SCRIPT_DIR%dist\%BUILD_NAME%.exe" "%SCRIPT_DIR%release\" >>"%LOG%" 2>&1
  ) else (
    echo [ERROR] dist\%BUILD_NAME%.exe not found>>"%LOG%"
    goto :showlog_err
  )
)

REM ================ POST-BUILD DIAGNOSTICS ============
for %%F in ("%SCRIPT_DIR%build\%BUILD_NAME%\warn-%BUILD_NAME%.txt") do (
  if exist "%%~fF" (
    echo.>>"%LOG%"
    echo [INFO] warn-%BUILD_NAME%.txt tail:>>"%LOG%"
    powershell -NoProfile -Command "Get-Content -Path '%%~fF' -Tail 200" >>"%LOG%" 2>&1
  )
)

echo.>>"%LOG%"
echo [INFO] Dist folder size:>>"%LOG%"
powershell -NoProfile -Command ^
  "$d=Get-ChildItem -Recurse -File '%SCRIPT_DIR%dist' -ErrorAction SilentlyContinue ^| Measure-Object -Property Length -Sum; '{0:N2} MB' -f ($d.Sum/1MB)" >>"%LOG%" 2>&1
echo [INFO] Release folder size:>>"%LOG%"
powershell -NoProfile -Command ^
  "$d=Get-ChildItem -Recurse -File '%SCRIPT_DIR%release' -ErrorAction SilentlyContinue ^| Measure-Object -Property Length -Sum; '{0:N2} MB' -f ($d.Sum/1MB)" >>"%LOG%" 2>&1

echo === BUILD END: %DATE% %TIME% ===>>"%LOG%"
echo.
if /I "%BUILD_MODE%"=="onedir" (
  echo [SUCCESS] Built release\%BUILD_NAME%\ (ONEDIR)
) else (
  echo [SUCCESS] Built release\%BUILD_NAME%.exe
)
echo.
echo ---- Tail of build_full.log ----
powershell -NoProfile -Command "Get-Content -Path '%LOG%' -Tail 200"
echo --------------------------------
pause
exit /b 0

:showlog_err
echo.
echo *** BUILD FAILED ***
echo ---- Tail of build_full.log ----
powershell -NoProfile -Command "Get-Content -Path '%LOG%' -Tail 200"
echo --------------------------------
pause
exit /b 1
