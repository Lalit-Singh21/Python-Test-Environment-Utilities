"""Generic windows automation functions"""
from pywinauto import win32defines, WindowNotFoundError
import pywinauto
import time
import sys
from PIL import ImageGrab
import datetime
import inspect
import win32com.client
import SendKeys

autoit = win32com.client.Dispatch("AutoItX3.Control")

def GetProductControl(parent, windowid):
    try:
        aWindowId = windowid.split("=")
        
        if aWindowId[0] == "window id":
            def ControlIdMatches(win): 
                return pywinauto.handleprops.controlid(win) == int(aWindowId[1])
            
            return parent.window_(predicate_func=ControlIdMatches)
        else:
            return parent[aWindowId[1]]
    except Exception, e:
        GetScreenshot()

def WinEdit_Set(control, fieldValue, check=True):
    """Set a WinEdit to the specified value

    By default it performs a check that the edit box value is correctly set
    """
    try:
        #LogMessage("WinEdit_Set " + fieldValue + " check=" + str(check))
        ControlReady(control)
        control.DrawOutline()
        control.Click()
        control.TypeKeys("{HOME}+{END}+{DEL}")
        control.SetText(fieldValue)
        control.TypeKeys("{TAB}")    
        if check:
            actualFieldValue = WinEdit_Get(control)
            
            if not compareField(fieldValue, actualFieldValue):
                raise Exception ("Tried to set control to \"" + fieldValue + "\" but it had the value \"" + actualFieldValue + "\"")
    except Exception, e:
        GetScreenshot()    

def WinEdit_Get(control):
    try:
        ControlReady(control)    
        return control.TextBlock()
    except Exception, e:
        GetScreenshot()    

def WinComboBox_Set(control, fieldValue, check=True):
    """ 
    Set a WinComboBox to the specified value
    By default it performs a check that the combo box value is correctly set
    """
    try:
        #LogMessage("WinComboBox_Set " + fieldValue)
        ControlReady(control)
        control.DrawOutline()
        control.Click()
        control.Select(fieldValue)
        control.Click()
        if check:
            selectedIndex = control.SelectedIndex()
            controlTexts = control.Texts()
            selectedText = controlTexts[selectedIndex + 1]
            
            if fieldValue != selectedText:
                raise Exception ("Tried to set control to \"" + fieldValue + "\" but it had the value \"" + selectedText + "\"")
    except Exception, e:
        GetScreenshot()        

def WinMultiComboBox_Check(control, fieldValue):
    #a bit tricky approach as dropdown is not recognized as list view
    try:
        ControlReady(control)
        control.DrawOutline()
        control.Click()
        control.TypeKeys("{F4}")
        SendKeys.SendKeys("+{F10}")
        SendKeys.SendKeys("{DOWN}")
        SendKeys.SendKeys("{DOWN}")
        SendKeys.SendKeys("{ENTER}")
        i = 0
        while fieldValue not in control.Texts():    
            for k in range (0,i-1,1):
                SendKeys.SendKeys("{DOWN}")
            SendKeys.SendKeys("{SPACE}")
            if fieldValue not in control.Texts():
                for k in range (0,i-1,1):
                    SendKeys.SendKeys("{DOWN}")            
                SendKeys.SendKeys("{SPACE}")
            i += 1    
    except Exception, e:
        GetScreenshot()

def WindowClose(control):
    try:    
        ControlReady(control)
        control.TypeKeys("%{F4}")
    except Exception, e:
        GetScreenshot()        


def HandleMWPopUp(control,text):
    try:
        dlg = control.window_(title="MarkitSERV MarkitWire")
        if dlg.Exists()and dlg.PopupWindow():
            DialogText = GetProductControl(dlg, 'name={0}'.format(text))
            if DialogText.Exists():
                ControlReady(dlg)
                dlg.DrawOutline()
                dlg.OKButton.Click()
    except Exception, e:
        GetScreenshot()
        
def CheckMWPopup(control):
    try:    
        dlg = control.window_(title="MarkitSERV MarkitWire")
        if dlg.Exists(): #or dlg.PopupWindow():
            return True
        else:
            return False
    except Exception, e:
        return False

def WinComboBox_Get(control):
    try:
        ControlReady(control)
        
        selectedIndex = control.SelectedIndex()
        
        controlTexts = control.Texts()
        
        selectedText = controlTexts[selectedIndex + 1]
        
        return selectedText
    except Exception, e:
        GetScreenshot()
    
def WinComboEdit_Set(control, fieldValue, check=True):
    try:
        #LogMessage("WinComboEdit_Set " + fieldValue)
        ControlReady(control)
        control.DrawOutline()
        control.TypeKeys("{HOME}+{END}+{DEL}")
        control.TypeKeys(fieldValue)
        control.TypeKeys("{TAB}")
    except Exception, e:
        GetScreenshot()

def WinCheckBox_Set(control, fieldValue):
    try:
        #LogMessage("WinCheckBox_Set " + str(fieldValue))
        
        ControlReady(control)
        control.DrawOutline()
        if fieldValue.lower() == 'true':
            expectedState = 1
        else:
            expectedState = 0
            
        actualState = control.GetCheckState()
        
        if actualState != expectedState:
            control.ClickInput()
    except Exception, e:
        GetScreenshot()
        
def WinButton_Click(control, method="ClickInput"):
    try:
        #LogMessage("WinButton_Click " + control.Class() + " " + method)        
        ControlReady(control)
        control.DrawOutline()
        if method == "ClickInput":
            control.ClickInput()
        else:
            control.Click()
    except Exception, e:
        GetScreenshot()
        
def WinButton_AutoItClick(title, button):
    try:
        buttonId = "[TEXT:" + button + "]"
        
        if autoit.ControlClick(title, "", buttonId) == 0:
           raise Exception ("Failed to click button")
    except Exception, e:
        GetScreenshot()
        
def WinMenu_Set(control, value):
    try:

        #LogMessage("WinMenu_Set " + value)        
        control.SetFocus()
        ControlReady(control)
        control.DrawOutline()
        if control.MenuItem(value).IsEnabled():
            result = control.MenuSelect(value)
            #LogMessage("WinMenu_Set result " + str(result))
            return True
        else:
            return False
    except Exception, e:
        LogMessage (e)

def WinMenu_Tick(control, value):
    try:
        #LogMessage("WinMenu_Set " + value)        
        control.SetFocus()
        ControlReady(control)
        control.DrawOutline()
        if not control.MenuItem(value).IsChecked():
            result = control.MenuSelect(value)
            #LogMessage("WinMenu_Tick result " + str(result))
            return True
        else:
            return False
    except Exception, e:
        LogMessage (e)

def WinMenu_TickCheck(control, value):
    try:
        #LogMessage("WinMenu_Set " + value)        
        control.SetFocus()
        ControlReady(control)
        control.DrawOutline()
        if control.MenuItem(value).IsChecked():
            return True
        else:
            return False
    except Exception, e:
        LogMessage (e)


def WinMenu_Check(control, value):
    try:
        #LogMessage("WinMenu_Set " + value)
        control.SetFocus()
        ControlReady(control)
        control.DrawOutline()
        if control.MenuItem(value).IsEnabled():
            return True
        else:
            return False
    except Exception, e:      
        LogMessage (e)
            

def WinMenu_Set2(control, value):
    try:
        
        #LogMessage("WinMenu_Set " + value)
        
        control.SetFocus()
        ControlReady(control)
        control.DrawOutline()
        #if control.MenuItem(value).IsEnabled():
        result = control.TypeKeys(value)
        #LogMessage("WinMenu_Set result " + str(result))
##            return True
##        else:
##            return False
        return True
    except Exception, e:      
        return False
    
def WinMenu_AutoItSet(title, value):
    try:
        aValue = value.split("->")
        
        a = autoit.WinGetText(title)
        
        if len(aValue) == 1:
            result = autoit.WinMenuSelectItem ( title, "", aValue[0])
        elif len(aValue) == 2:
            result = autoit.WinMenuSelectItem ( title, "", aValue[0], aValue[1]) 
        elif len(aValue) == 3:
            result = autoit.WinMenuSelectItem ( title, "", aValue[0], aValue[1], aValue[2])
        elif len(aValue) == 4:
            result = autoit.WinMenuSelectItem ( title, "", aValue[0], aValue[1], aValue[2], aValue[3])
        elif len(aValue) == 5:
            result = autoit.WinMenuSelectItem ( title, "", aValue[0], aValue[1], aValue[2], aValue[3], aValue[4])
        
        if result == 0:
           raise Exception ("Failed to click menu: " + value)
    except Exception, e:
        GetScreenshot()
        
def WinTab_Select(control, value):
    Number_of_Retry = 0
    while Number_of_Retry <= 5:    
        try:
            #LogMessage("WinTab_Select " + control.Class() + " " + value)
            control.DrawOutline()
            control.Select(value)
            break
        except Exception, e:
            Number_of_Retry += 1
            if Number_of_Retry == 5:
                GetScreenshot()
            continue
        
def WindowReady(parent, windowTitle):
    Number_of_Retry = 0
    while Number_of_Retry <= 5:    
        try:
            #LogMessage("Wait for window with title " + windowTitle)
            i = 0
            while i < 300:
                if parent.window_(title=windowTitle).Exists():
                    ControlReady(parent.window_(title=windowTitle))
                    break
                else:
                    time.sleep(0.1)
                    i+= 1
                if i == 300:
                    GetScreenshot()
            return parent.window_(title=windowTitle)
            break
        except Exception, e:
            Number_of_Retry += 1
            if Number_of_Retry == 5:
                GetScreenshot()
            continue
        
def ControlReady(control):
    Number_of_Retry = 0
    while Number_of_Retry <= 5:    
        try:
            control.SetFocus()
            control.Wait('enabled')
            control.Wait('visible')
            control.VerifyActionable()
            break
        except Exception, e:
            Number_of_Retry += 1
            if Number_of_Retry == 5:
                GetScreenshot()
            continue

def SetField(control, fieldType, fieldValue):
    #LogMessage("SetField " + control.Class() + " " + fieldType + " " + fieldValue)
    try:
        if fieldType == 'edit':
            WinEdit_Set(control, fieldValue)
        elif fieldType == 'combobox' :
            WinComboBox_Set(control, fieldValue)
        elif fieldType == 'calendar' or fieldType == 'comboeditbox':
            WinComboEdit_Set(control, fieldValue)
        elif fieldType == 'checkbox':
            WinCheckBox_Set(control, fieldValue)
        elif fieldType == 'button':
            WinButton_Click(control)
        else:
            raise Exception ("unrecognised value for fieldType: " + fieldType)
            GetScreenshot()
    except Exception, e:
        print e
        return False
        
def GetField(control, fieldType):
    #LogMessage("GetField " + control.Class() + " " + fieldType)
    try    :
        if fieldType == 'edit':
            return WinEdit_Get(control)
        elif fieldType == 'combobox' :
            return WinComboBox_Get(control)
        else:
            raise Exception ("unrecognised value for fieldType: " + fieldType)
            GetScreenshot()
    except Exception, e:
        print e
        return False
        
def LogMessage(text):
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ": " + str(text)
    pass


def compareField(expected, actual):
    try:
        expected = formatFinancial(expected)
        
        actual = formatFinancial(actual)
            
        return expected == actual
    except Exception, e:
        GetScreenshot()
        
def formatFinancial(value):
    try:    
        if is_financial(value):
            value = value.replace(',','')
            
            value = float(value)
            
            value = "%.4f" % value
            
            return value
        else:
            return value
    except Exception, e:
        GetScreenshot()
        
def is_financial(value):
    try:
        value = value.replace(',','')
        
        return is_number(value)
    except Exception, e:
        print e
        
def is_number(value):
    try:
        float(value)
        return True
    except ValueError:       
        return False

def WinListView_GetRowCount(control):
    try:
        rowCount = control.ItemCount()
        
        return str(rowCount)
    except Exception, e:
        GetScreenshot()    

def WinListView_Scroll(control):
    ##scroll listview
    try:
        control.SendMessage(win32defines.WM_VSCROLL, win32defines.SB_LINEDOWN)
    except Exception,e:
        GetScreenshot()        
        print e
    
    
def WinListView_GetGridData(control, includeColumnString=""):
    try:
        data = []
        
        includeColumnNames = includeColumnString.split(";")
        includeColumn      = []
        
        columnCount     = control.ColumnCount()
        columnNamesList = control.Columns()
        #print columnNamesList
        columnNames     = []
        
        rowCount        = control.ItemCount()
        
        #LogMessage("Folder Row Count = " + str(rowCount))
        
        # Construct a list of the column names
        for col in range(0, columnCount):
            columnNames.append(columnNamesList[col]["text"])
            
            if columnNames[col] in includeColumnNames:
                includeColumn.append(True)
            else:
                includeColumn.append(False)
        
        # Get the data from the grid control
        rawData = control.Items()
        
        # construct a List where each row is represented by a Dictionary
        # the data comes from the control in a flat list
        # e.g. "row 1 column 1", "row 1 column 2", "row 1 column 3", "row 2 column 1", "row 2 column 2"
        # so we have to calculate the current index in the List with (row * columnCount) + col
        for row in range(0, rowCount):
            data.append({})
            
            for col in range(0, columnCount):
                if includeColumn[col]:
                    field = columnNames[col]
                    value = rawData[(row * columnCount) + col]["text"]
                    
                    data[row][field] = value
        
        # dispay the result in the logs
        #for row in data:
        #    LogMessage("Data = " + str(row))
        # 
        return data
    except Exception, e:
        GetScreenshot()

def GetScreenshot():
    function_name = inspect.stack()[1][3]	
    filename = "{0}{1}_{2}.jpg".format(ErrorScreenshot,function_name,(datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")))
    ImageGrab.grab().save(filename,"JPEG")
    sys.exit()


def SetOutputDir(dir):    
    global ErrorScreenshot
    ErrorScreenshot = dir
