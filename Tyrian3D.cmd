@echo off
rem Starts the game built by tools\build_windows.bat. It runs in build\game, where it keeps its
rem settings and saves (opentyrian.cfg, tyrian.cfg, tyrian.sav).
setlocal
cd /d "%~dp0build\game"
if not exist tyrian3d.exe (echo no build\game\tyrian3d.exe: run tools\build_windows.bat first & pause & exit /b 1)
start "" tyrian3d.exe %*
