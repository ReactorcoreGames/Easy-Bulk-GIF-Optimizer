@echo off
echo ========================================
echo Easy Bulk GIF Optimizer - Build Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or later from python.org
    pause
    exit /b 1
)

echo [1/5] Checking dependencies...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

echo.
echo [2/5] Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Easy-Bulk-GIF-Optimizer.spec" del "Easy-Bulk-GIF-Optimizer.spec"

echo.
echo [3/5] Building executable...
pyinstaller ^
    --name "Easy-Bulk-GIF-Optimizer" ^
    --onefile ^
    --windowed ^
    --icon="assets/icon.ico" ^
    --add-data "gifski;gifski" ^
    --add-data "assets;assets" ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=ttkbootstrap ^
    --hidden-import=PIL.Image ^
    --exclude-module matplotlib ^
    --exclude-module numpy ^
    --exclude-module pandas ^
    --exclude-module scipy ^
    --exclude-module pytest ^
    --noconfirm ^
    main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [4/5] Creating release folder...
if not exist "RELEASE" mkdir RELEASE
copy "dist\Easy-Bulk-GIF-Optimizer.exe" "RELEASE\" >nul
copy "readme.md" "RELEASE\" >nul
if not exist "RELEASE\gifski" mkdir "RELEASE\gifski"
copy "gifski\gifski.exe" "RELEASE\gifski\" >nul
copy "gifski\GIFSKI README.md" "RELEASE\gifski\" >nul

echo.
echo [5/5] Cleaning up temporary files...
rmdir /s /q build

echo.
echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo.
echo Output location: RELEASE\Easy-Bulk-GIF-Optimizer.exe
echo.
echo Release folder contains:
echo   - Easy-Bulk-GIF-Optimizer.exe  [Main executable]
echo   - readme.md                     [User documentation]
echo   - gifski\gifski.exe             [GIF encoder]
echo   - gifski\GIFSKI README.md       [Gifski credits]
echo.
echo IMPORTANT: Test the executable before distributing!
echo.
pause
