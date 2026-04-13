@echo off
echo Setting up Project Brain...

REM Create folder structure
mkdir raw\architecture 2>nul
mkdir raw\signals 2>nul
mkdir raw\conversations 2>nul
mkdir raw\research 2>nul
mkdir wiki\layers 2>nul
mkdir wiki\components 2>nul
mkdir wiki\people 2>nul
mkdir wiki\concepts 2>nul
mkdir wiki\gaps 2>nul
mkdir outputs\posts 2>nul
mkdir outputs\reports 2>nul
mkdir outputs\predictions 2>nul

echo.
echo Folders created.
echo.
echo Project Brain is ready.
echo.
echo Next steps:
echo   1. Open a terminal in this folder
echo   2. Run: claude
echo   3. Paste the wake-up prompt from GETTING-STARTED.md
echo.
pause
