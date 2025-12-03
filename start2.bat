@echo off
setlocal enabledelayedexpansion

:: 定义关键变量（便于维护）
set "CHROME_REG_PATH=HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
set "USER_DATA_DIR=%~dp0tmp"  :: Chrome temporary user data directory (avoid space issues)
set "WEB_PORT=5001"
set "INDEX_HTML_PATH=%~dp0index.html"
set "HTTP_SERVER_EXE=http_sever.exe"  :: Note: Typo in original script - http_sever → http_server (modify as needed)

:: ===================== Step 1: Find Chrome browser path =====================
set "chrome_path="
:: Query registry (compatible with 32/64-bit systems)
for /f "tokens=2* delims=:" %%A in ('reg query "%CHROME_REG_PATH%" /ve 2^>nul') do (
    :: Extract registry value (handle spaces/special characters)
    set "tmp_val=%%B"
    :: Remove leading/trailing spaces
    for /f "tokens=*" %%C in ("!tmp_val!") do set "tmp_chrome_path=%%C"
    
    :: Verify path exists (compatible with paths containing spaces)
    if exist "!tmp_chrome_path!" (
        set "chrome_path=!tmp_chrome_path!"
        goto :ChromeFound  :: Exit loop immediately after finding to improve efficiency
    )
)

:: ===================== Step 2: Handle logic when Chrome not found =====================
:ChromeNotFound
echo [ERROR] Chrome browser not found!
echo [INFO] Starting local web server (Port: %WEB_PORT%)...

:: Check if web server program exists
if not exist "%HTTP_SERVER_EXE%" (
    echo [ERROR] %HTTP_SERVER_EXE% does not exist, cannot start web server!
    pause
    exit /b 1
)

:: Start web server (run in background to avoid blocking)
start /b "" "%HTTP_SERVER_EXE%" -port %WEB_PORT%

:: Wait for server startup (1-second delay to avoid access before server is ready)
timeout /t 1 /nobreak >nul

:: Open with default browser and wait for closure
echo [INFO] Opening default browser to: http://127.0.0.1:%WEB_PORT%
start "" /WAIT http://127.0.0.1:%WEB_PORT%

:: Stop web server (optional: enable if http_server.exe does not exit automatically when port is occupied)
:: taskkill /f /im %HTTP_SERVER_EXE% >nul 2>&1
goto :End

:: ===================== Step 3: Handle logic when Chrome is found =====================
:ChromeFound
echo [INFO] Chrome browser path: "%chrome_path%"

:: Create Chrome temporary user data directory (avoid permission issues)
if not exist "%USER_DATA_DIR%" (
    mkdir "%USER_DATA_DIR%" >nul 2>&1
)

:: Start Chrome (disable cross-origin restrictions, open local index.html)
echo [INFO] Starting Chrome (cross-origin security disabled)...
start "" "%chrome_path%" ^
    --disable-web-security ^
    --disable-features=CrossSiteDocumentBlockingIfIsolating ^
    --user-data-dir="%USER_DATA_DIR%" ^
    "file:///%INDEX_HTML_PATH%"

:: ===================== End =====================
:End
echo [INFO] Operation completed!
endlocal
pause >nul