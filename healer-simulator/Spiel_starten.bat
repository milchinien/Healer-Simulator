@echo off
rem Startet den Healer Simulator direkt mit der installierten Godot-Version (ohne Editor).
set GODOT=%USERPROFILE%\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64.exe
if not exist "%GODOT%" (
  echo Godot wurde nicht gefunden: %GODOT%
  echo Bitte den Pfad in dieser Datei anpassen.
  pause
  exit /b 1
)
start "" "%GODOT%" --path "%~dp0."
