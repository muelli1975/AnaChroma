@echo off
color 06
setlocal EnableExtensions EnableDelayedExpansion

set "BASEDIR=%~dp0"
set "TOOLSDIR=%BASEDIR%tools"

set "FFMPEG=%TOOLSDIR%\ffmpeg.exe"
set "CJPEG=%TOOLSDIR%\cjpeg.exe"
set "EXIFTOOL=%TOOLSDIR%\exiftool.exe"
set "CIELABDIR=%TOOLSDIR%\cielab"
set "CIELAB=%CIELABDIR%\cielab.exe"

set "OUTDIR=%BASEDIR%output"
set "TMPDIR=%OUTDIR%\tmp"
set "QUALITY=90"

if not exist "%OUTDIR%" mkdir "%OUTDIR%"
if not exist "%TMPDIR%" mkdir "%TMPDIR%"

if "%~1"=="" (
    echo Dateien oder Ordner auf diese Batch ziehen.
    pause
    exit /b
)

echo.
echo Groesse waehlen:
echo 1 = Original
echo 2 = 1080p
echo 3 = 2160p
echo 4 = 2048 lange Seite
echo.
set /p SIZECHOICE=Bitte 1-4 eingeben:

if "%SIZECHOICE%"=="1" (
    set "SCALEPART="
) else if "%SIZECHOICE%"=="2" (
    set "SCALEPART=,scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd+full_chroma_int"
) else if "%SIZECHOICE%"=="3" (
    set "SCALEPART=,scale=3840:2160:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd+full_chroma_int"
) else if "%SIZECHOICE%"=="4" (
    set "SCALEPART=,scale=2048:2048:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd+full_chroma_int"
) else (
    echo Ungueltige Eingabe.
    pause
    exit /b
)

echo.
echo Matrix waehlen:
echo 1  = Dubois LCD (Sanders/McAllister) + rot
echo 2  = Dubois
echo 3  = Optimized (Peter Wimmer)
echo 4  = Cosima AnaglyphType=3 - Optimierter Farbraum ohne Kompromisse beim Ghosting (Gerhard P. Herbig)
echo 5  = Cosima AnaglyphType=4 - Optimierter Farbraum mit etwas beigemischter Echtfarbe (Gerhard P. Herbig)
echo 6  = Compromise (Jure Ahtik)
echo 7  = iaian7 Anachrome (John Einselen)
echo 8  = Rendepth (Andres Hernandez)
echo 9  = Rendepth 2 (Andres Hernandez)
echo 10 = Color
echo 11 = Half-Color
echo 12 = Grey
echo 13 = Oldschool
echo 14 = Frans van den Poel
echo 15 = John Wattie
echo 16 = CIELab Least Squares (David McAllister)
echo 17 = Dubois gruen/magenta (GM)
echo 18 = Dubois amber/blau (YB)
echo.
echo Mehrfachauswahl moeglich, z. B.:
echo 1,3,5
echo 1-5
echo 1-5,8,10
echo.
set /p MATRIXCHOICE=Bitte 1-18 oder Bereiche eingeben:

call :parse_matrix_choices "%MATRIXCHOICE%"
if errorlevel 1 (
    echo Ungueltige Eingabe.
    pause
    exit /b
)

REM =========================
REM COUNT INPUT FILES
REM =========================

set COUNT=0

for %%F in (%*) do (
    if exist "%%~fF\" (
        call :count_folder "%%~fF"
    ) else (
        set /a COUNT+=1
    )
)

if "%COUNT%"=="0" (
    echo Keine Dateien gefunden.
    pause
    exit /b
)

set "SOURCECOUNT=%COUNT%"
set /a COUNT=SOURCECOUNT*METHODCOUNT

REM =========================
REM PROCESS INPUTS
REM =========================

set INDEX=0

for %%F in (%*) do (
    if exist "%%~fF\" (
        call :process_folder "%%~fF"
    ) else (
        call :process_methods_for_file "%%~fF" ""
    )
)

rmdir /s /q "%TMPDIR%"

title Fertig
echo.
echo Fertig.
pause
exit /b

REM =========================
REM MATRIX CHOICE PARSER
REM =========================

:parse_matrix_choices
set "RAWCHOICE=%~1"
set "RAWCHOICE=%RAWCHOICE: =%"
if not defined RAWCHOICE exit /b 1

for /L %%N in (1,1,18) do set "SEL_%%N="

for %%T in (%RAWCHOICE:,= %) do (
    set "TOKEN=%%~T"
    set "TOKEN=!TOKEN:"=!"
    if not defined TOKEN exit /b 1

    for /f "tokens=1,2 delims=-" %%A in ("!TOKEN!") do (
        set "RSTART=%%~A"
        set "REND=%%~B"
    )

    if defined REND (
        set /a TEST1=RSTART+0 >nul 2>&1
        if errorlevel 1 exit /b 1
        set /a TEST2=REND+0 >nul 2>&1
        if errorlevel 1 exit /b 1

        if !RSTART! LSS 1 exit /b 1
        if !RSTART! GTR 18 exit /b 1
        if !REND! LSS 1 exit /b 1
        if !REND! GTR 18 exit /b 1

        if !RSTART! LEQ !REND! (
            for /L %%N in (!RSTART!,1,!REND!) do set "SEL_%%N=1"
        ) else (
            for /L %%N in (!RSTART!,-1,!REND!) do set "SEL_%%N=1"
        )
    ) else (
        set /a TEST1=TOKEN+0 >nul 2>&1
        if errorlevel 1 exit /b 1
        if !TOKEN! LSS 1 exit /b 1
        if !TOKEN! GTR 18 exit /b 1
        set "SEL_!TOKEN!=1"
    )
)

set "METHODLIST="
set METHODCOUNT=0
for /L %%N in (1,1,18) do (
    if defined SEL_%%N (
        set "METHODLIST=!METHODLIST! %%N"
        set /a METHODCOUNT+=1
    )
)

if not defined METHODLIST exit /b 1
exit /b 0

REM =========================
REM MATRIX DEFINITIONS
REM =========================

:set_matrix_definition
if "%~1"=="1" (
    set "MATRIXNAME=dubois_lcd"
    set "MATRIXMODE=linear"
    set "MATRIX_LEFT=0.4561:0.500484:0.176381:0:-0.0400822:-0.0378246:-0.0157589:0:-0.0152161:-0.0205971:-0.00546856:0"
    set "MATRIX_RIGHT=-0.0434706:-0.0879388:-0.00155529:0:0.378476:0.73364:-0.0184503:0:-0.0721527:-0.112961:1.2264:0"
    set "POSTFIX=,lutrgb=r='gammaval(0.75)'"
    exit /b
)

if "%~1"=="2" (
    set "MATRIXNAME=dubois"
    set "MATRIXMODE=linear"
    set "MATRIX_LEFT=0.437:0.449:0.164:0:-0.062:-0.062:-0.024:0:-0.048:-0.05:-0.017:0"
    set "MATRIX_RIGHT=-0.011:-0.032:-0.007:0:0.377:0.761:-0.009:0:-0.026:-0.093:1.234:0"
    set "POSTFIX="
    exit /b
)

if "%~1"=="3" (
    set "MATRIXNAME=wimmer"
    set "MATRIXMODE=srgb"
    set "MATRIX_LEFT=0:0.7:0.3:0:0:0:0:0:0:0:0:0"
    set "MATRIX_RIGHT=0:0:0:0:0:1:0:0:0:0:1:0"
    set "POSTFIX=,lutrgb=r='gammaval(0.6666667)'"
    exit /b
)

if "%~1"=="4" (
    set "MATRIXNAME=cosima3"
    set "MATRIXMODE=linear"
    set "MATRIX_LEFT=0.299:0.587:0.114:0:0:0:0:0:0:0:0:0"
    set "MATRIX_RIGHT=0:0:0:0:0.299:0.701:0:0:0.299:0:0.701:0"
    set "POSTFIX=,lutrgb=r='gammaval(0.75)'"
    exit /b
)

if "%~1"=="5" (
    set "MATRIXNAME=cosima4"
    set "MATRIXMODE=linear"
    set "MATRIX_LEFT=0.6495:0.2935:0.057:0:0:0:0:0:0:0:0:0"
    set "MATRIX_RIGHT=0:0:0:0:0.1495:0.8505:0.057:0:0.1495:0.057:0.8505:0"
    set "POSTFIX=,lutrgb=r='gammaval(0.75)'"
    exit /b
)

if "%~1"=="6" (
    set "MATRIXNAME=compromise"
    set "MATRIXMODE=srgb"
    set "MATRIX_LEFT=0.439:0.447:0.148:0:0:0:0:0:0:0:0:0"
    set "MATRIX_RIGHT=0:0:0:0:0.095:0.934:-0.005:0:-0.018:-0.028:1.057:0"
    set "POSTFIX="
    exit /b
)

if "%~1"=="7" (
    set "MATRIXNAME=iaian7"
    set "MATRIXMODE=iaian7"
    exit /b
)

if "%~1"=="8" (
    set "MATRIXNAME=rendepth"
    set "MATRIXMODE=rendepth"
    set "MATRIX_LEFT=0.4561:0.500484:0.176381:0:-0.0400822:-0.0378246:-0.0157589:0:-0.0152161:-0.0205971:-0.00546856:0"
    set "MATRIX_RIGHT=-0.0434706:-0.0879388:-0.00155529:0:0.378476:0.73364:-0.0184503:0:-0.0721527:-0.112961:1.2264:0"
    set "POSTFIX=,lutrgb=r='gammaval(0.625)':g='gammaval(1.25)'"
    exit /b
)

if "%~1"=="9" (
    set "MATRIXNAME=rendepth2"
    set "MATRIXMODE=rendepth"
    set "MATRIX_LEFT=0.439:0.447:0.148:0:0:0:0:0:0:0:0:0"
    set "MATRIX_RIGHT=0:0:0:0:0.095:0.934:-0.028:0:-0.018:-0.005:1.057:0"
    set "POSTFIX=,lutrgb=r='gammaval(0.625)':g='gammaval(1.25)'"
    exit /b
)

if "%~1"=="10" (
    set "MATRIXNAME=color"
    set "MATRIXMODE=srgb"
    set "MATRIX_LEFT=1:0:0:0:0:0:0:0:0:0:0:0"
    set "MATRIX_RIGHT=0:0:0:0:0:1:0:0:0:0:1:0"
    set "POSTFIX="
    exit /b
)

if "%~1"=="11" (
    set "MATRIXNAME=halfcolor"
    set "MATRIXMODE=srgb"
    set "MATRIX_LEFT=0.299:0.587:0.114:0:0:0:0:0:0:0:0:0"
    set "MATRIX_RIGHT=0:0:0:0:0:1:0:0:0:0:1:0"
    set "POSTFIX="
    exit /b
)

if "%~1"=="12" (
    set "MATRIXNAME=grey"
    set "MATRIXMODE=srgb"
    set "MATRIX_LEFT=0.299:0.587:0.114:0:0:0:0:0:0:0:0:0"
    set "MATRIX_RIGHT=0:0:0:0:0.299:0.587:0.114:0:0.299:0.587:0.114:0"
    set "POSTFIX="
    exit /b
)

if "%~1"=="13" (
    set "MATRIXNAME=oldschool"
    set "MATRIXMODE=srgb"
    set "MATRIX_LEFT=0.299:0.587:0.114:0:0:0:0:0:0:0:0:0"
    set "MATRIX_RIGHT=0:0:0:0:0.299:0.587:0.114:0:0:0:0:0"
    set "POSTFIX="
    exit /b
)

if "%~1"=="14" (
    set "MATRIXNAME=vdp"
    set "MATRIXMODE=srgb"
    set "MATRIX_LEFT=0.5:0.5:0:0:0:0:0:0:0:0:0:0"
    set "MATRIX_RIGHT=0:0:0:0:0.4:0.6:0:0:0.2:0:0.8:0"
    set "POSTFIX="
    exit /b
)

if "%~1"=="15" (
    set "MATRIXNAME=wattie"
    set "MATRIXMODE=srgb"
    set "MATRIX_LEFT=0.8:0.2:0.2:0:0:0:0:0:0:0:0:0"
    set "MATRIX_RIGHT=0:0:0:0:0.2:0.8:0:0:0.1:0:0.9:0"
    set "POSTFIX="
    exit /b
)

if "%~1"=="16" (
    set "MATRIXNAME=cielab"
    set "MATRIXMODE=cielab"
    exit /b
)

if "%~1"=="17" (
    set "MATRIXNAME=dubois_gm"
    set "MATRIXMODE=linear"
    set "MATRIX_LEFT=-0.062:-0.158:-0.039:0:0.284:0.668:0.143:0:-0.015:-0.027:0.021:0"
    set "MATRIX_RIGHT=0.529:0.705:0.024:0:-0.016:-0.015:-0.065:0:0.009:0.075:0.937:0"
    set "POSTFIX="
    exit /b
)

if "%~1"=="18" (
    set "MATRIXNAME=dubois_yb"
    set "MATRIXMODE=linear"
    set "MATRIX_LEFT=1.062:-0.205:0.299:0:-0.026:0.908:0.068:0:-0.038:-0.173:0.022:0"
    set "MATRIX_RIGHT=-0.016:-0.123:-0.017:0:0.006:0.062:-0.017:0:0.094:0.185:0.911:0"
    set "POSTFIX="
    exit /b
)

exit /b 1

REM =========================
REM PROGRESS HELPERS
REM =========================

:set_steps_for_mode
set "FILESTEPS=3"
if /i "%MATRIXMODE%"=="cielab" set "FILESTEPS=5"
exit /b

:draw_progress
setlocal EnableDelayedExpansion
set "CURFILE=%~1"
set "TOTALFILES=%~2"
set "STEP=%~3"
set "STEPS=%~4"
set "DISPLAYNAME=%~5"
set "TITLETEXT=%~6"

if "!TOTALFILES!"=="0" set "TOTALFILES=1"
if "!STEPS!"=="0" set "STEPS=1"

set /a DONEUNITS=((CURFILE-1)*STEPS)+STEP
set /a TOTALUNITS=TOTALFILES*STEPS
set /a PCT=DONEUNITS*100/TOTALUNITS
set /a FILLED=PCT*30/100

set "BAR="
for /l %%A in (1,1,!FILLED!) do set "BAR=!BAR!#"
for /l %%A in (!FILLED!+1,1,30) do set "BAR=!BAR!-"

title !PCT!%% - [!CURFILE!/!TOTALFILES!] !TITLETEXT!
echo [!BAR!] !PCT!%%  Datei !CURFILE!/!TOTALFILES!  -  !DISPLAYNAME!
endlocal
exit /b

REM =========================
REM COUNT FOLDER
REM =========================

:count_folder
set "INPUTDIR=%~f1"
if "%INPUTDIR:~-1%"=="\" set "INPUTDIR=%INPUTDIR:~0,-1%"

for /r "%INPUTDIR%" %%F in (*.jpg *.jpeg *.png *.tif *.tiff *.bmp *.webp) do (
    set /a COUNT+=1
)
exit /b

REM =========================
REM PROCESS FOLDER
REM =========================

:process_folder
set "INPUTDIR=%~f1"
if "%INPUTDIR:~-1%"=="\" set "INPUTDIR=%INPUTDIR:~0,-1%"
set "ROOTNAME=%~nx1"

for /r "%INPUTDIR%" %%F in (*.jpg *.jpeg *.png *.tif *.tiff *.bmp *.webp) do (
    set "FULLDIR=%%~dpF"
    set "RELDIR=!FULLDIR:%INPUTDIR%\=!"

    if /i "!RELDIR!"=="%%~dpF" (
        set "TARGETSUBDIR=%ROOTNAME%"
    ) else (
        if "!RELDIR:~-1!"=="\" set "RELDIR=!RELDIR:~0,-1!"
        set "TARGETSUBDIR=%ROOTNAME%\!RELDIR!"
    )

    call :process_methods_for_file "%%~fF" "!TARGETSUBDIR!"
)
exit /b

:process_methods_for_file
set "THISFILE=%~1"
set "THISSUBDIR=%~2"

for %%M in (%METHODLIST%) do (
    call :set_matrix_definition %%M
    set /a INDEX+=1
    call :process_file "%THISFILE%" "%THISSUBDIR%"
)
exit /b

REM =========================
REM PROCESS FILE
REM =========================

:process_file
set "INFILE=%~1"
set "SUBDIR=%~2"
set "NAME=%~n1"
set "JOBTAG=%INDEX%_%RANDOM%%RANDOM%"

call :set_steps_for_mode

if defined SUBDIR (
    if not exist "%OUTDIR%\%SUBDIR%" mkdir "%OUTDIR%\%SUBDIR%"
    set "TMPFILE=%TMPDIR%\%JOBTAG%_%NAME%.ppm"
    set "OUTTMP=%TMPDIR%\%JOBTAG%_%NAME%_%MATRIXNAME%.__tmp__.jpg"
    set "OUTFILE=%OUTDIR%\%SUBDIR%\%NAME%_%MATRIXNAME%.jpg"
    set "LEFTPNG=%TMPDIR%\%JOBTAG%_%NAME%_left.png"
    set "RIGHTPNG=%TMPDIR%\%JOBTAG%_%NAME%_right.png"
    set "OUTPNG=%TMPDIR%\%JOBTAG%_%NAME%_%MATRIXNAME%.png"
) else (
    set "TMPFILE=%TMPDIR%\%JOBTAG%_%NAME%.ppm"
    set "OUTTMP=%TMPDIR%\%JOBTAG%_%NAME%_%MATRIXNAME%.__tmp__.jpg"
    set "OUTFILE=%OUTDIR%\%NAME%_%MATRIXNAME%.jpg"
    set "LEFTPNG=%TMPDIR%\%JOBTAG%_%NAME%_left.png"
    set "RIGHTPNG=%TMPDIR%\%JOBTAG%_%NAME%_right.png"
    set "OUTPNG=%TMPDIR%\%JOBTAG%_%NAME%_%MATRIXNAME%.png"
)

if "%MATRIXMODE%"=="linear" (
    set "VF=format=gbrp16,split[l][r]; [l]crop=iw/2:ih:0:0,zscale=transferin=iec61966-2-1:transfer=linear,colorchannelmixer=%MATRIX_LEFT%[left]; [r]crop=iw/2:ih:iw/2:0,zscale=transferin=iec61966-2-1:transfer=linear,colorchannelmixer=%MATRIX_RIGHT%[right]; [left][right]blend=all_mode=addition,zscale=transferin=linear:transfer=iec61966-2-1%POSTFIX%%SCALEPART%,format=rgb24"
)

if "%MATRIXMODE%"=="rendepth" (
    set "VF=format=gbrp16,split[l][r]; [l]crop=iw/2:ih:0:0,colorchannelmixer=%MATRIX_LEFT%,lutrgb=r='clip(val,0,maxval)':g='clip(val,0,maxval)':b='clip(val,0,maxval)'[left]; [r]crop=iw/2:ih:iw/2:0,colorchannelmixer=%MATRIX_RIGHT%,lutrgb=r='clip(val,0,maxval)':g='clip(val,0,maxval)':b='clip(val,0,maxval)'[right]; [left][right]blend=all_mode=addition%POSTFIX%%SCALEPART%,format=rgb24"
)

if "%MATRIXMODE%"=="srgb" (
    set "VF=format=gbrp16,split[l][r]; [l]crop=iw/2:ih:0:0,colorchannelmixer=%MATRIX_LEFT%[left]; [r]crop=iw/2:ih:iw/2:0,colorchannelmixer=%MATRIX_RIGHT%[right]; [left][right]blend=all_mode=addition%POSTFIX%%SCALEPART%,format=rgb24"
)

if "%MATRIXMODE%"=="iaian7" (
    set "VF=format=gbrp16,split[l][r]; [l]crop=iw/2:ih:0:0,colorchannelmixer=0.4:0.3:0.3:0:0:0:0:0:0:0:0:0,lutrgb=r='gammaval(0.87)':g='gammaval(0.87)':b='gammaval(0.87)'[left]; [r]crop=iw/2:ih:iw/2:0,colorchannelmixer=0:0:0:0:0.1:0.9:0:0:0.1:0:0.9:0,lutrgb=r='gammaval(1.176)':g='gammaval(1.176)':b='gammaval(1.176)'[right]; [left][right]blend=all_mode=addition,colorchannelmixer=1.16:-0.08:-0.08:0:-0.02:1.04:-0.02:0:-0.02:-0.02:1.04:0%SCALEPART%,format=rgb24"
)

if "%MATRIXMODE%"=="cielab" (
    set "SPLITFILTER_L=crop=iw/2:ih:0:0"
    set "SPLITFILTER_R=crop=iw/2:ih:iw/2:0"

    if "%SIZECHOICE%"=="2" (
        set "SPLITFILTER_L=!SPLITFILTER_L!,scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd+full_chroma_int"
        set "SPLITFILTER_R=!SPLITFILTER_R!,scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd+full_chroma_int"
    ) else if "%SIZECHOICE%"=="3" (
        set "SPLITFILTER_L=!SPLITFILTER_L!,scale=3840:2160:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd+full_chroma_int"
        set "SPLITFILTER_R=!SPLITFILTER_R!,scale=3840:2160:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd+full_chroma_int"
    ) else if "%SIZECHOICE%"=="4" (
        set "SPLITFILTER_L=!SPLITFILTER_L!,scale=2048:2048:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd+full_chroma_int"
        set "SPLITFILTER_R=!SPLITFILTER_R!,scale=2048:2048:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd+full_chroma_int"
    )

    call :draw_progress %INDEX% %COUNT% 1 %FILESTEPS% "%NAME%" "CIELab: links - %NAME%"
    "%FFMPEG%" -y -loglevel error -i "%INFILE%" -frames:v 1 -vf "!SPLITFILTER_L!" "%LEFTPNG%" >nul 2>&1
    if errorlevel 1 (
        del "%LEFTPNG%" >nul 2>&1
        del "%RIGHTPNG%" >nul 2>&1
        del "%OUTPNG%" >nul 2>&1
        del "%OUTTMP%" >nul 2>&1
        del "%TMPFILE%" >nul 2>&1
        exit /b
    )

    call :draw_progress %INDEX% %COUNT% 2 %FILESTEPS% "%NAME%" "CIELab: rechts - %NAME%"
    "%FFMPEG%" -y -loglevel error -i "%INFILE%" -frames:v 1 -vf "!SPLITFILTER_R!" "%RIGHTPNG%" >nul 2>&1
    if errorlevel 1 (
        del "%LEFTPNG%" >nul 2>&1
        del "%RIGHTPNG%" >nul 2>&1
        del "%OUTPNG%" >nul 2>&1
        del "%OUTTMP%" >nul 2>&1
        del "%TMPFILE%" >nul 2>&1
        exit /b
    )

    call :draw_progress %INDEX% %COUNT% 3 %FILESTEPS% "%NAME%" "CIELab: berechne - %NAME%"
    "%CIELAB%" "%LEFTPNG%" "%RIGHTPNG%" -o "%OUTPNG%" >nul 2>&1
    if errorlevel 1 (
        del "%LEFTPNG%" >nul 2>&1
        del "%RIGHTPNG%" >nul 2>&1
        del "%OUTPNG%" >nul 2>&1
        del "%OUTTMP%" >nul 2>&1
        del "%TMPFILE%" >nul 2>&1
        exit /b
    )

    call :draw_progress %INDEX% %COUNT% 4 %FILESTEPS% "%NAME%" "CIELab: JPEG - %NAME%"
    "%CJPEG%" -quality %QUALITY% -sample 1x1 -optimize "%OUTPNG%" > "%OUTTMP%" 2>nul
    if errorlevel 1 (
        del "%LEFTPNG%" >nul 2>&1
        del "%RIGHTPNG%" >nul 2>&1
        del "%OUTPNG%" >nul 2>&1
        del "%OUTTMP%" >nul 2>&1
        del "%TMPFILE%" >nul 2>&1
        exit /b
    )

    call :draw_progress %INDEX% %COUNT% 5 %FILESTEPS% "%NAME%" "CIELab: Speichern (EXIF) - %NAME%"
    if exist "%EXIFTOOL%" (
        "%EXIFTOOL%" -overwrite_original -TagsFromFile "%INFILE%" --Preview:all "%OUTTMP%" >nul 2>&1
    )

    move /Y "%OUTTMP%" "%OUTFILE%" >nul
    del "%LEFTPNG%" >nul 2>&1
    del "%RIGHTPNG%" >nul 2>&1
    del "%OUTPNG%" >nul 2>&1
    del "%TMPFILE%" >nul 2>&1

    exit /b
)

call :draw_progress %INDEX% %COUNT% 1 %FILESTEPS% "%NAME%" "FFmpeg - %NAME%"
"%FFMPEG%" -y -loglevel error -i "%INFILE%" -frames:v 1 -vf "%VF%" "%TMPFILE%" >nul 2>&1
if errorlevel 1 (
    del "%TMPFILE%" >nul 2>&1
    del "%OUTTMP%" >nul 2>&1
    del "%LEFTPNG%" >nul 2>&1
    del "%RIGHTPNG%" >nul 2>&1
    del "%OUTPNG%" >nul 2>&1
    exit /b
)

call :draw_progress %INDEX% %COUNT% 2 %FILESTEPS% "%NAME%" "JPEG - %NAME%"
"%CJPEG%" -quality %QUALITY% -sample 1x1 -optimize "%TMPFILE%" > "%OUTTMP%" 2>nul
if errorlevel 1 (
    del "%TMPFILE%" >nul 2>&1
    del "%OUTTMP%" >nul 2>&1
    del "%LEFTPNG%" >nul 2>&1
    del "%RIGHTPNG%" >nul 2>&1
    del "%OUTPNG%" >nul 2>&1
    exit /b
)

call :draw_progress %INDEX% %COUNT% 3 %FILESTEPS% "%NAME%" "Speichern (EXIF) - %NAME%"
if exist "%EXIFTOOL%" (
    "%EXIFTOOL%" -overwrite_original -TagsFromFile "%INFILE%" --Preview:all "%OUTTMP%" >nul 2>&1
)

move /Y "%OUTTMP%" "%OUTFILE%" >nul
del "%TMPFILE%" >nul 2>&1
del "%LEFTPNG%" >nul 2>&1
del "%RIGHTPNG%" >nul 2>&1
del "%OUTPNG%" >nul 2>&1

exit /b

