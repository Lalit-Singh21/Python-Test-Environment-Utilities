REM--This batch file will uninstall Python 2.7.1 and its package in unattended mode

@ Echo off
cls


::wmic product get name
::product where name="" call uninstall /nointeractive
::wmic:root\cli>product where name="" uninstall /uninteractive


::WMI Uninstallation
Echo this is uninstalling WMI-py2.7.....
X:\_Applications\PyCOM\UninstallW.exe /f WMI-py2.7
@ping 123.45.67.89 -n 1 -w %1000 > nul
@ping 123.45.67.89 -n 1 -w %1000 > nul
start X:\_Applications\PyCOM\ClickToUninstall.exe
@ping 123.45.67.89 -n 1 -w %1000 > nul
@ping 123.45.67.89 -n 1 -w %1000 > nul

::LXML uninstallation
Echo this is uninstalling lxml-py2.7.....
X:\_Applications\PyCOM\UninstallW.exe /f lxml-py2.7
@ping 123.45.67.89 -n 1 -w %1000 > nul
@ping 123.45.67.89 -n 1 -w %1000 > nul
start X:\_Applications\PyCOM\ClickToUninstall.exe
@ping 123.45.67.89 -n 1 -w %1000 > nul
@ping 123.45.67.89 -n 1 -w %1000 > nul

::PYWIN32 uninstallation
Echo this is uninstalling pywin32-py2.7.....
X:\_Applications\PyCOM\UninstallW.exe /f pywin32-py2.7
@ping 123.45.67.89 -n 1 -w %1000 > nul
@ping 123.45.67.89 -n 1 -w %1000 > nul
start X:\_Applications\PyCOM\ClickToUninstall.exe
@ping 123.45.67.89 -n 1 -w %1000 > nul
@ping 123.45.67.89 -n 1 -w %1000 > nul


::cx_Oracle-5.1-10g.win32-py2.7 uninstallation
echo This Will Proceed with uninstallation of X:\_Applications\PyCOM\cx_Oracle-5.1-10g.win32-py2.7.msi please do not turn off your computer
c:\Windows\System32\msiexec.exe /uninstall  X:\_Applications\X:\_Applications\PyCOM\cx_Oracle-5.1-10g.win32-py2.7.msi /QN /LWAMOE C:\msi.log
echo cx_Oracle WAS successfully uninstalled from this machine

::Python 2.7.1 uninstallation
echo This Will Proceed with uninstallation of Python 2.7.1 please do not turn off your computer
c:\Windows\System32\msiexec.exe /uninstall  X:\_Applications\PyCOM\python-2.7.1.msi /QN /LWAMOE C:\msi.log
echo Python WAS successfully uninstalled from this machine


::deleting environment variables for Python

reg delete HKCU\Environment\ /v SW_UNIT_TEST_SRCROOT /f
reg delete HKCU\Environment\ /v PYTHONPATH /f
reg delete HKCU\Environment\ /v PATH /f
reg delete HKCU\Environment\ /v SW_TRACE_FILE /f
echo Python environment Variables deleted successfully

RD /S /Q C:\Python27

PAUSE


