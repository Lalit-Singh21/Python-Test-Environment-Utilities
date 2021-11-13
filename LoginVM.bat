@Echo Off
call %NFT_HOME%env.bat
set SCRIPT_DIR=W:\NFT\tools\win\TempCleanup\

@REM Run Method #4: Login Machines 
rem=======================================================================================================================================================================================
rem execute below command if you want to restart a range of VMs
rem c:\python27\python.exe %SCRIPT_DIR%\PythonUtilities.py RestartMachines -fm "LON14MSTST001" -lm "LON14MSTST010"

rem execute below command if you want to restart a single VM
rem c:\python27\python.exe %SCRIPT_DIR%\PythonUtilities.py LoginMachines -fm "mswin7tst001" -lm "mswin7tst002" -cw "close"
c:\python27\python.exe %SCRIPT_DIR%\PythonUtilities.py LoginMachines -fm "mswin7tst023" -cw "close"
rem c:\python27\python.exe %SCRIPT_DIR%\PythonUtilities.py RestartMachines -login "yes" -cw "dontclose" -fm mswin7tst023


rem when using customized config file to read the list of VM (default config filepath is \\ukrobot\QTPEnv\MarkitWire_QTP\SupportApps\PythonUtilities\PyUtilities_Configuration.cfg)
rem c:\python27\python.exe %SCRIPT_DIR%\PythonUtilities.py LoginMachines -os "win7" -cw "clos" -c "N:\Perforce\testing\MarkitWire_QTP\SupportApps\PythonUtilities\PyUtilities_Configuration.cfg"
rem c:\python27\python.exe %SCRIPT_DIR%\PythonUtilities.py LoginMachines -cw dontlogin -c N:\Perforce\testing\MarkitWire_QTP\SupportApps\PythonUtilities\PyUtilities_Configuration.cfg
rem=======================================================================================================================================================================================

@Echo On

pause
