#Region ;**** Directives created by AutoIt3Wrapper_GUI ****
#AutoIt3Wrapper_Res_requestedExecutionLevel=asInvoker
#EndRegion ;**** Directives created by AutoIt3Wrapper_GUI ****
; Automate Login on Win XP and Win 7 Machines
;set up command line variables variables

$Close = $CMDLINE[1]
if $CMDLINE[0] = 1 Then
	$servername = $Close
	$Close = "close"
Else
	$servername= $CMDLINE[2]
EndIf

;set up other program variables
$username = "nft"
$password = "nft"
$WinOS = ""
$ps="W:\NFT\tools\win\AutomaticLogin\PSTools\PsExec.exe"
$lockCmdXP="C:\WINDOWS\system32\rundll32.exe user32.dll, LockWorkStation"
$lockCmdWin7="C:\WINDOWS\sysWOW64\rundll32.exe user32.dll, LockWorkStation"


Global $oMyError = ObjEvent("AutoIt.Error","MyErrFunc")
;----------------------------------------------------------------------------------------------------------
; Com Error Handler
;----------------------------------------------------------------------------------------------------------
Func MyErrFunc()
	Local $HexNumber
	Local $strMsg

	$HexNumber = Hex($oMyError.Number, 8)
	$strMsg = "Error Number: " & $HexNumber & @CRLF
	$strMsg &= "WinDescription: " & $oMyError.WinDescription & @CRLF
	$strMsg &= "Script Line: " & $oMyError.ScriptLine & @CRLF
	MsgBox(0, "ERROR", $strMsg)
	SetError(1)
Endfunc


Func _WinWaitActivate($title,$text,$timeout=100)
	WinWait($title,$text,$timeout)
	If Not WinActive($title,$text) Then WinActivate($title,$text)
	WinWaitActive($title,$text,$timeout)
	If WinActivate($title,$text) then return True
EndFunc

;ensure machine is up and get its OS name
_WaitForIP($servername)

Func _WaitForIP($sIP)
	$Count=0
	Do
		$Ping = Ping($sIP,1)
		Sleep(1000) ; Give the CPU a break
		$Count=$Count+1
		If $Ping Then
;~ 		   MsgBox(0,"Ping",$Ping)
			$WinOS = RegRead("\\"&$sIP&"\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductName")
			if StringRegExp($WinOS,"XP") Then
				$WinOS="XP"
			ElseIf StringRegExp($WinOS,"7") Then
				$WinOS="WIN7"
			ElseIf StringRegExp($WinOS,"2008") Then
				$WinOS="2008"
			ElseIf StringRegExp($WinOS,"2003") Then
				$WinOS="2003"
			EndIf
		EndIf
	 Until $WinOS == "XP" OR $WinOS =="WIN7" OR $WinOS =="2003" OR $WinOS =="2008" OR $Count=120
;~ 	 MsgBox(0,"OS",$WinOS)
	If $WinOS == "XP" OR $WinOS =="WIN7" OR $WinOS =="2003" OR $WinOS =="2008" Then
		_HandlePopUp()
		_VMLogin()
	Else
		Exit
	EndIf
EndFunc   ;==>_WaitForIP

Func _HandlePopUp()
	;check for TightVNC popups if present then close them
	$errorWinText="TightVNC info,TightVNC error,TightVNC authentication info,New TightVNC Connection,Standard VNC Authentication"
	$arrpopup= StringSplit($errorWinText, ",")
	for $i=1 to $arrpopup[0]
		$popup=True
		While $popup=True
			If WinExists($arrpopup[$i], "") Then
				WinClose($arrpopup[$i], "")
			Else
				$popup=False
			EndIf
		WEnd
	Next
EndFunc	 ;==>_HandlePopUp


Func _VMLogin()
	Run ("W:\NFT\software\win\VNC\vncviewer.exe")
	Sleep (1000)
	If _WinWaitActivate("New TightVNC Connection","") Then
		Send ($servername)
		Send("{ENTER}")
	EndIf
	Sleep (2000)
	If _WinWaitActivate("Standard VNC Authentication","") Then
		Send($password)
		Send("{ENTER}")
	EndIf
	Sleep (2000)
	If not StringRegExp($Close,"dontlogin") Then
		If $WinOS = "XP" Then
			$command= $ps & ' \\' &$servername & ' -u ' &$username & ' -p ' &$password & ' ' &$lockCmdXP
			Run($command)
			If _WinWaitActivate($servername,"") Then
				Sleep(2000)
				Send ("{ENTER}")
				Sleep(1000)
				Send ("{ESC}")
				Sleep(1000)
				Send ("{SHIFTDOWN}{CTRLDOWN}{ALTDOWN}{DELETE}" & "{SHIFTUP}{CTRLUP}{ALTUP}")
				Sleep(2000)
				Send ("{SPACE}")
				Send ("{SPACE}")
				Sleep(500)
				Send ("{ALTDOWN}u{ALTUP}"& $username)
				Sleep(500)
				Send("{ALTDOWN}p{ALTUP}"& $password)
				Sleep(500)
				Send ("{ENTER}")
				Send ("{ESC}")
				sleep (7000)
			EndIf
		ElseIf $WinOS = "WIN7_Automation" Then
			If _WinWaitActivate($servername,"") Then
				Sleep(5000)
				Send ("{SHIFTDOWN}{CTRLDOWN}{ALTDOWN}{DELETE}" & "{SHIFTUP}{CTRLUP}{ALTUP}")
				Sleep(5000)
				Send("{TAB}")
				Send ("{SPACE}")
				Sleep (2000)
				Send ("{SPACE}")
				Sleep(1000)
				Send ("{BACKSPACE}")
				Send($password)
				Sleep(1000)
				Send ("{ENTER}")
				Sleep(8000)
			 EndIf
		  ElseIf $WinOS = "2008" OR $WinOS = "Win7" Then
			If _WinWaitActivate($servername,"") Then
				Sleep(5000)
				Send ("{SHIFTDOWN}{CTRLDOWN}{ALTDOWN}{DELETE}" & "{SHIFTUP}{CTRLUP}{ALTUP}")
				Sleep(9000)
				Send("{RIGHT}")
				Sleep (3000)
				Send ("{SPACE}")
				Sleep(2000)
				Send ("{BACKSPACE}")
				Send($password)
				Sleep(2000)
				Send ("{ENTER}")
				Sleep(8000)
			EndIf
		EndIf ;os
	EndIf    ;==>dontlogin
	If StringRegExp($Close,"close") Then
		;Run("C:\WINDOWS\system32\taskkill.exe /f /im vncviewer*")
		WinClose($servername)
	EndIf
EndFunc   ;==>_VM_Login

Exit ; to exit the AutoIt Process


