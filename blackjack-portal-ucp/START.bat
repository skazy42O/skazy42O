@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title BLACK JACK - Portal ^& UCP
cd /d "%~dp0"

rem ============================================================
rem  BLACK JACK RolePlay - Portal i UCP (lokalno na Windows-u)
rem  Radi iz bilo kog foldera, npr. D:\blackjack-portal-ucp
rem ============================================================

set "PORT=8080"
set "PHP="
set "MYSQL="

rem --- trazi PHP ---
for %%P in ("%~dp0php\php.exe" "C:\xampp\php\php.exe" "D:\xampp\php\php.exe") do (
  if not defined PHP if exist "%%~P" set "PHP=%%~P"
)
if not defined PHP (
  for /d %%D in ("C:\laragon\bin\php\*" "D:\laragon\bin\php\*") do (
    if not defined PHP if exist "%%~D\php.exe" set "PHP=%%~D\php.exe"
  )
)
if not defined PHP (
  where php >nul 2>nul && set "PHP=php"
)

rem --- trazi MySQL klijent ---
for %%M in ("C:\xampp\mysql\bin\mysql.exe" "D:\xampp\mysql\bin\mysql.exe") do (
  if not defined MYSQL if exist "%%~M" set "MYSQL=%%~M"
)
if not defined MYSQL (
  for /d %%D in ("C:\laragon\bin\mysql\*" "D:\laragon\bin\mysql\*") do (
    if not defined MYSQL if exist "%%~D\bin\mysql.exe" set "MYSQL=%%~D\bin\mysql.exe"
  )
)
if not defined MYSQL (
  where mysql >nul 2>nul && set "MYSQL=mysql"
)

if not exist "app\config.php" (
  copy /y "app\config.sample.php" "app\config.php" >nul
  echo  [i] Napravljen app\config.php - upisi podatke baze ^(opcija 4^).
)

:menu
echo.
echo  ==================================================
echo            BLACK JACK RolePlay - Portal ^& UCP
echo  ==================================================
if defined PHP   (echo   PHP:   !PHP!) else (echo   PHP:   NIJE PRONADJEN - instaliraj XAMPP)
if defined MYSQL (echo   MySQL: !MYSQL!) else (echo   MySQL: nije pronadjen)
echo  --------------------------------------------------
echo   1. Pokreni sajt  ^(http://127.0.0.1:%PORT%^)
echo   2. Uvezi bazu iz .sql fajla
echo   3. Proveri da li config odgovara bazi
echo   4. Izmeni config ^(baza, IP servera...^)
echo   5. Izlaz
echo  --------------------------------------------------
set "CH="
set /p "CH=  Izaberi [1-5]: "
if "%CH%"=="1" goto run
if "%CH%"=="2" goto import
if "%CH%"=="3" goto check
if "%CH%"=="4" goto config
if "%CH%"=="5" exit /b 0
goto menu

:needphp
echo.
echo  [!] PHP nije pronadjen. Instaliraj XAMPP ^(https://www.apachefriends.org^)
echo      na C:\xampp ili D:\xampp, pa pokreni START.bat ponovo.
pause
goto menu

:run
if not defined PHP goto needphp
"%PHP%" -m | findstr /i "pdo_mysql" >nul || (
  echo  [!] PHP nema pdo_mysql. U php.ini skini ; ispred extension=pdo_mysql
  pause
  goto menu
)
echo.
echo  Sajt radi na http://127.0.0.1:%PORT%  - zatvori ovaj prozor da ugasis.
echo  MySQL ^(XAMPP Control Panel - Start MySQL^) mora biti upaljen.
start "" "http://127.0.0.1:%PORT%/"
"%PHP%" -S 127.0.0.1:%PORT% -t public
goto menu

:import
if not defined MYSQL (
  echo  [!] MySQL klijent nije pronadjen ^(XAMPP: C:\xampp\mysql\bin\mysql.exe^).
  pause
  goto menu
)
set "SQLF=%USERPROFILE%\Downloads\blackjack11.09.2026.sql"
echo.
echo  Putanja do .sql fajla ^(Enter = !SQLF!^)
set /p "IN=  > "
if defined IN set "SQLF=!IN:"=!"
set "IN="
if not exist "!SQLF!" (
  echo  [!] Fajl ne postoji: !SQLF!
  pause
  goto menu
)
set "DBN=blackjack"
set /p "IN=  Ime baze ^(Enter = blackjack^): "
if defined IN set "DBN=!IN!"
set "IN="
set "DBU=root"
set /p "IN=  MySQL korisnik ^(Enter = root^): "
if defined IN set "DBU=!IN!"
set "IN="
echo  Lozinka MySQL-a ^(za XAMPP je prazna - samo Enter^):
"%MYSQL%" -u "!DBU!" -p -e "CREATE DATABASE IF NOT EXISTS `!DBN!` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci" || (pause & goto menu)
echo  Uvozim... ^(moze potrajati^) - unesi lozinku ponovo:
"%MYSQL%" -u "!DBU!" -p --default-character-set=utf8mb4 "!DBN!" < "!SQLF!" && (
  echo  [OK] Baza je uvezena u "!DBN!".
  echo       U app\config.php proveri: 'name' =^> '!DBN!', 'user' =^> '!DBU!'
) || echo  [!] Uvoz nije uspeo.
pause
goto menu

:check
if not defined PHP goto needphp
"%PHP%" tools\proveri-bazu.php > "proveri-bazu.txt"
type "proveri-bazu.txt"
echo.
echo  Rezultat je sacuvan u proveri-bazu.txt ^(nema podataka igraca - mozes da ga posaljes^).
pause
goto menu

:config
start "" notepad "app\config.php"
goto menu
