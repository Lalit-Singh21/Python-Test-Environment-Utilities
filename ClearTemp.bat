@Echo Off

call W:\NFT\env.bat

@REM Create a variable for script location. keeps things tidy
set SCRIPT_DIR=W:\NFT\tools\win\TempCleanup
title = Delete temp files older than 12 hours (%temp%)
@REM Clear Temp 

rem=================================================================================================================================================
rem when using config file to read the list of vm 
c:\python27\python.exe %SCRIPT_DIR%\PythonUtilities.py ClearTemp -t "C$\Users\nft\AppData\Local\Temp" -gettemp yes -c PyUtilities_Configuration.cfg

rem=================================================================================================================================================


@Echo On




