@echo off
logman stop NFTPerfLog

FOR /F "usebackq" %%i IN (`hostname`) DO SET PCNAME=%%i

echo>%PCNAME%
dir /b/l %PCNAME%>X
set /p PCNAME=<X

del X
del %PCNAME%

rem echo result path: %NFT_TEST_RESULTS%%1%
move c:\Logs\perfmon_basic_%PCNAME%.csv %NFT_TEST_RESULTS%%1%

