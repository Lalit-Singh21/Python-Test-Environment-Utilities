How to use the script:
1) If called from command prompt--> \\scriptdirectory\WinLogin_VNC.exe close VMName 
or               -->\\scriptdirectory\WinLogin_VNC.exe VMName 
-->parameter help:
   ->>"Close" is a flag which specify to close the vnc session, (If don't want to close the VNC session then dont pass it or pass any other string except "close")
   ->>VMName is a full machine name like lon14mstst001

2) Automatically revoked from REstart VM batch file with if below parameters are passed :

c:\python27\python.exe %SCRIPT_DIR%\PythonUtilities.py RestartMachines -login "yes" -cw "close" -c "N:\Perforce\testing\MarkitWire_QTP\SupportApps\PythonUtilities\PyUtilities_Configuration.cfg"

Parameter help:

-login "yes" : if want to login VMS after restart (default value is No)
-cw "close": if want to close window after login (default value is close, if dont want to close window then provide any other string)


3) If called from Batch file only for login

c:\python27\python.exe %SCRIPT_DIR%\PythonUtilities.py LoginMachines -cw "o" -c "N:\Perforce\testing\MarkitWire_QTP\SupportApps\PythonUtilities\PyUtilities_Configuration.cfg"

-cw "close": if want to close window after login (default value is close, if dont want to close window then provide any other string)



Note: config file and machine name (or machine names in range can be passed to the scripts)

Eg:
c:\python27\python.exe %SCRIPT_DIR%\PythonUtilities.py LoginMachines -fm "mswin7tst001" -lm "mswin7tst002" -cw "dontclose"
c:\python27\python.exe %SCRIPT_DIR%\PythonUtilities.py LoginMachines -fm "lon14mstst035" -cw "dontclose"


c:\python27\python.exe %SCRIPT_DIR%\PythonUtilities.py RestartMachines -login "yes" -cw "close" -fm "mswin7tst001" -lm "mswin7tst002"
c:\python27\python.exe %SCRIPT_DIR%\PythonUtilities.py RestartMachines -login "yes" -cw "close" -fm "mswin7tst001"