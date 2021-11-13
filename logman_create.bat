@echo off
rem set output directory
set dir=C:\Logs
mkdir %dir%
FOR /F "usebackq" %%i IN (`hostname`) DO SET PCNAME=%%i

echo>%PCNAME%
dir /b/l %PCNAME%>X
set /p PCNAME=<X
echo %PCNAME%
del X
del %PCNAME%

rem -s <computer>         remote machine
rem -si <[[hh:]mm:]ss>    sample interval (default 15s)
rem logman create counter NFTPerfLog -si 00:15 -cf counterlist.txt -f csv -v mmddhhmm -o %dir%\perfmon_basic_%PCNAME%
logman create counter NFTPerfLog -si 00:15 -cf counterlist.txt -f csv --v -o %dir%\perfmon_basic_%PCNAME%
