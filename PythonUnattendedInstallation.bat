@echo off
echo.
echo +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
echo This is the automated installation Batch for Python Packages
echo +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
echo.


::Installing Python
::###############################################################################################
echo This Will Proceed with The Silent installation of Python 2.7.1 please do not turn off your computer
echo Copying python-2.7.1.msi in local drive...
xcopy /R X:\_Applications\PyCOM\python-2.7.1.msi C:\ /y
ECHO copied python-2.7.1.msi successfully
echo.
echo ++++++++++++++++++++++++++++++++
echo Step 1. Installing Python 2.7.1 
echo ++++++++++++++++++++++++++++++++
echo.
echo Please stand by .......
C:\Windows\System32\msiExec.exe -i C:\python-2.7.1.msi /QN /LWAMOE C:\msi.log

del C:\python-2.7.1.msi 
echo deleted the python-2.7.1.msi file successfully from local drive
if errorlevel 0 echo Python Installation completed successfully.
if errorlevel 1 echo Python Installation failed.

::###############################################################################################


::installing cx_Oracle package
::###############################################################################################
echo This Will Proceed with The Silent installation of cx_Oracle-5.1-10g.win32-py2 please do not turn off your computer
echo.
echo ++++++++++++++++++++++++++++++++++++++++++++++
echo Step 2. Installing cx_Oracle-5.1-10g.win32-py2
echo ++++++++++++++++++++++++++++++++++++++++++++++
echo.
echo Please stand by .......
C:\Windows\System32\msiExec.exe -i X:\_Applications\PyCOM\cx_Oracle-5.1-10g.win32-py2.7.msi /QN /LWAMOE C:\msi.log
ECHO CX_Oracle WAS successfully installed in this machine
if errorlevel 0 echo cx_Oracle-5.1-10g.win32-py2 Installation completed successfully.
if errorlevel 1 echo cx_Oracle-5.1-10g.win32-py2 Installation failed.
::###############################################################################################



::copying ply-3.4 and executing setup.py
::###############################################################################################
echo.
echo +++++++++++++++++++++++++++++++++++++++++++++++++++
echo Step 3. COpying ply-3.4 file and executing setup.py
echo +++++++++++++++++++++++++++++++++++++++++++++++++++
echo.
mkdir C:\Python27\ply-3.4
xcopy /s/e/y X:\_Applications\PyCOM\ply-3.4 C:\Python27\ply-3.4 /I
echo copied ply-3.4 successfully
cd C:\Python27\ply-3.4\
setup.py install
echo setup.py successfully installed
::###############################################################################################



::copying pycparser and executing setup.py
::###############################################################################################
echo.
echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
echo Step 4. COpying pycparser-2.04 file and executing setup.py
echo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
echo.
mkdir C:\Python27\pycparser-2.04
xcopy /s/e/y X:\_Applications\PyCOM\pycparser-2.04 C:\Python27\pycparser-2.04 /I
ECHO copied pycparser-2.04 successfully
cd C:\Python27\pycparser-2.04\
setup.py install
echo setup.py successfully installed
::###############################################################################################



::setting the environment variables
::###############################################################################################
echo.
echo ++++++++++++++++++++++++++++++++++++++++++
echo Step 5. setting the environment variables
echo ++++++++++++++++++++++++++++++++++++++++++
echo.
echo setting environment variable for SW_UNIT_TEST_SRCROOT ...
reg add HKCU\Environment /v SW_UNIT_TEST_SRCROOT /d "C:\PyCOM" /f
ECHO user environment variable for SW_UNIT_TEST_SRCROOT has been set successfully

echo setting environment variable for PYTHONPATH ...
reg add HKCU\Environment /v PYTHONPATH /d "C:\Python27;C:\PYCOM\bin;C:\PYCOM\py_srcroot;C:\PYCOM\qtp" /f
ECHO user environment variable for PYTHONPATH has been set successfully

echo setting environment variable for PATH...
reg add HKCU\Environment /v PATH /d "C:\Python27;C:\PYCOM\bin;C:\PYCOM\lib;C:\PYCOM\py_srcroot" /f
ECHO user environment variable for PATH has been set successfully

echo setting environment variable for SW_TRACE_FILE 
reg add HKCU\Environment /v SW_TRACE_FILE /d "C:\Logs" /f
ECHO user environment variable for SW_TRACE_FILE has been set successfully
::###############################################################################################



::installing other Packages (LXML,WMI.PyWIN)
::###############################################################################################
echo This Will Proceed with other python packages please do not turn off your computer
echo.
echo +++++++++++++++++++++++++++++++++++++++
echo Step 6. Installing LXML, WMI and PyWIN
echo +++++++++++++++++++++++++++++++++++++++
echo.
start X:\_Applications\PyCOM\PySilent.exe
ECHO Python packages got successfully installed 
::###############################################################################################



::Enabling trace collector
::###############################################################################################
echo.
echo +++++++++++++++++++++++++++++++++++++++++
echo Step 7. Enabling the Trace Collector Logs
echo +++++++++++++++++++++++++++++++++++++++++
echo.
del /F /S /Q C:\Builds\PyCOM\*.*
RD /S /Q C:\PyCOM
call X:\Builds\PyCOM\PyCOM_CopyToLocal.bat SW_9_0_140650

call X:\Builds\PyCOM\PyCOM_DoEverything.bat SW_9_0_140650

start C:\Python27\Lib\site-packages\pythonwin\Pythonwin.exe
C:\PyCOM\qtp\pyapi_com.py --debug
ECHO Trace Collector logs enabled successfully
::###############################################################################################

::Close the batch file automatically
::cls
::@exit
pause
date
