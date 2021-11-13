import time
import pywinauto 
import tc_control
import ConfigParser
import os
import traceback
from productOr import controlWindowId
from user_admin.user import User
from csvTradeData import csvTradeData
import nft_tc_client

class TCSession(object):
    """Class for a tc_client session, including start of app, login, and functions

       Pass the path to the tc_client exe, and the connect host name (assume port 9009)
    """

    # for folder selection, either by direct access or key shortcuts
    folders = { 
                "Direct": ("&View->Folder->Direct Deals*", "%V+F+F+{ENTER}+{ENTER}"),
                "Novations": ("&View->Folder->Novations*", "%V+F+F+N+{ENTER}+{ENTER}"),
                "Active" : ("&View->Folder->Active Deals*", "%V+F+F+A+A+A+{ENTER}+{ENTER}"),
                "Brokered": ("&View->Folder->Brokered Deals*", "%V+F+F+B+{ENTER}+{ENTER}"),
                "Exercise": ("&View->Folder->Exercise*", "%V+F+F+E+{ENTER}+{ENTER}")
              }

    def __init__(self, screenshot_dir,db,
                 tc_path = 'C:\Clients\SW_10_0_179232/tc_client.exe',
                 host = "testvip08"):
        self.TC_UpdateINI(tc_path, host)
        self.pywin = pywinauto.application.Application()
        self.pywin.Start_(tc_path)
        tc_control.SetOutputDir(screenshot_dir)
        self.receivers = {}
        self.user= ""
        self.db_name=db
        
    def TC_UpdateINI(self,config_path, host, port="9009"):
        bResult = False
        host_section = r"/Transport/Client"
        try:
            ConfigPath = config_path.replace("exe","ini")
            if not os.path.exists(ConfigPath):
                open(ConfigPath,'w').close()
            config = ConfigParser.RawConfigParser(allow_no_value=True)
            config.read(ConfigPath)
            if host_section not in config.sections():
                #adding section /Transport/Client
                config.add_section(host_section)
                with open(ConfigPath, 'w') as configfile:
                    config.write(configfile)
                bResult = True
            #adding host/port in section /Transport/Client
            config.set(host_section, ";T&H {0}".format(host[-1]),)              
            config.set(host_section, 'host', host)
            config.set(host_section, 'port', port)                      
            with open(ConfigPath, 'w') as configfile:
                config.write(configfile)
                bResult = True                
        except Exception, e:
            print e
        return bResult


    def TC_Login(self, username):
        """Login user with tc_client"""
        retry = 0
        while retry <= 5: 
            try:
                # Create a user object
                self.user = User(username,self.db_name)                              
                # login, password always = username 
                tc_control.WinEdit_Set(self.pywin["MarkitSERV MarkitWire Logon"]["User Name:Edit"], username)
                tc_control.WinEdit_Set(self.pywin["MarkitSERV MarkitWire Logon"]["Password:Edit"], username, check=False)
                #tc_control.WinButton_Click(self.pywin["MarkitSERV MarkitWire Logon"]["OKButton"])
                tc_control.WinButton_AutoItClick("MarkitSERV MarkitWire Logon","OK")

                # window titles for use with functions
                full_name = self.user.get_property("full_name")
                self.main_win_title = "MarkitSERV MarkitWire [" + full_name + "]"
                self.compose_win_title = "Compose New Deal - MarkitSERV MarkitWire [" + full_name + "]"
                self.amend_win_title = "Compose Amendment - MarkitSERV MarkitWire [" + full_name + "]"
                self.uniamend_win_title = "Compose Unilateral Amendment - MarkitSERV MarkitWire [" + full_name + "]"
                self.compose_find_equity = "Find Equity"
                mainWin=tc_control.WindowReady(self.pywin, self.main_win_title)
                mainWin.Maximize()
                control = tc_control.GetProductControl(mainWin,"name=ReadyStatusBar")   
                tc_control.ControlReady(control)
                controlTexts = ""
                iCount = 0
                while controlTexts != "Ready":
                    control.DrawOutline()
                    controlTexts = control.GetPartText(0)
                    time.sleep(0.1)
                    iCount += 1
                    if iCount == 300 :
                        break                 
                break

            except Exception, e:
                if retry == 5:
                    raise Exception (e)
                    tc_control.GetScreenshot()
                retry += 1
                print "Failed login attempt {0}".format(retry)
                continue
        
    def ControlFromOR(self,parent, name):
        try:
            windowId = controlWindowId(name)
            return tc_control.GetProductControl(parent, windowId)
        except Exception, e:
            print e

    def ControlFromSubWinOR(self,parent, name):
        try:
            windowId = subWinControlWindowId(name)
            return tc_control.GetProductControl(parent, windowId)
        except Exception, e:
            print e

    def TC_FindEquity(self):
        return tc_control.WindowReady(self.pywin, self.compose_find_equity)

    def TC_ComposeWindow(self):
        return tc_control.WindowReady(self.pywin, self.compose_win_title)

    def TC_ComposeAmendmentWindow(self):
        return tc_control.WindowReady(self.pywin, self.amend_win_title)

    def TC_ComposeUniAmendmentWindow(self):
        return tc_control.WindowReady(self.pywin, self.uniamend_win_title)
    
    def TC_ComposeWindowTitle(self):
        return tc_control.WindowReady(self.pywin, self.compose_win_title)

    def TC_MainWindow(self):
        return tc_control.WindowReady(self.pywin, self.main_win_title)

    def TC_AddDataHandler(self,  modifyData):
        composeWindow = self.TC_ComposeWindow()
        tabControl = composeWindow["&Message:TabControl"]        
        currentTab = ""
        for m in modifyData.split(";"):
            field = m.split(":=")[0]
            value = m.split(":=")[1]
            aField = field.split("|")
            fieldTab = aField[0]
            fieldName = aField[0] + "|" + aField[1]
            fieldType = aField[2]
            if fieldTab != currentTab:
                tc_control.WinTab_Select(tabControl, fieldTab)
                currentTab = fieldTab                
            control = self.ControlFromOR(composeWindow, fieldName)
            tc_control.SetField(control, fieldType, value)

    def TC_SelectAddresses(self, receiver, composeWindow, skipParticipant=False):
        try:
            # commented out for now - needs changing to get rid of Community stuff        
            #composeWindow = tc_control.WindowReady(self.compose_, title)
            #to_button=tc_control.GetProductControl(composeWindow, "name=T&o...")
            #self.username = receiver
            self.receivers[receiver] = User(receiver,self.db_name)
            if receiver in self.receivers:
                self.receiver = self.receivers[receiver]
            else:
                self.receivers[receiver] = User(receiver,self.db_name)
            full_name = self.receivers[receiver].get_property("full_name")
            group_name = self.receivers[receiver].get_property("group_name")
            to_participant = tc_control.GetProductControl(composeWindow, "name=T&o...")
            tc_control.WinButton_Click(to_participant)
            #tc_control.WinButton_AutoItClick(self.compose_win_title, "T&o...")
            selectAddresses = tc_control.WindowReady(self.pywin, "Select Addresses")
            if not skipParticipant:
                tc_control.WinEdit_Set(selectAddresses["&Participant:Edit"], group_name)        
            tc_control.WinEdit_Set(selectAddresses["&Addressee:Edit"], full_name)
            #tc_control.WinButton_Click(selectAddresses["&To ->"])
            #tc_control.WinButton_AutoItClick("Select Addresses", "&To ->")
            select_participant = tc_control.GetProductControl(selectAddresses, "name=&To ->")
            tc_control.WinButton_Click(select_participant)
            tc_control.WinButton_Click(selectAddresses["OK"])
            #tc_control.WinButton_AutoItClick("Select Addresses", "OK")
        except Exception, e:
            print e

        
    def TC_SetCreateData(self, composeWindow, tradeData):
        try:
            #composeWindow = self.TC_ComposeWindow(user)
            tradeData = csvTradeData(tradeData)
            #print tradeData.tradeDataKeys()
            for field in tradeData.createData(0):
                # Handle fields not related to searching in a subwin
                if field != "Create|Search..." and field != "Create|$SubWin":
                    control = self.ControlFromOR(composeWindow, field)
                    fieldData = tradeData.createData(0)[field]
                    tc_control.SetField(control, fieldData['Type'], fieldData['Value'])
                elif field == "Create|Search...":
                    control = self.ControlFromOR(composeWindow, field)
                    fieldData = tradeData.createData(0)[field]
                    if fieldData['Value'].lower()=="true":
                        tc_control.SetField(control, fieldData['Type'], fieldData['Value'])                                        
                        self.TC_PopulateSubWin(tradeData)
        except Exception, e:
            print e


    def TC_PopulateSubWin(self, tradeData):
        try:
            subWindow = self.TC_FindEquity()
            menuOptions = {
                'Equity Name':({tc_control.WinEdit_Set:'name=Name:Edit'},),
                'Equity RIC':({tc_control.WinEdit_Set:'name=RIC:Edit'},),
                'Search':({tc_control.WinButton_Click:'name=&SearchButton'},),
                'OK':({tc_control.WinButton_Click:'name=OKButton'},)
                }
            for field in tradeData.subWinData(0):
                fieldData = tradeData.subWinData(0)[field]
                option=field.split("|")[1]
                if option in menuOptions:
                    for proc in menuOptions[option]:
                        for func,para in proc.items():
                            control = tc_control.GetProductControl(subWindow, para)
                            func(control,fieldData["Value"]) 
        except Exception, e:
            print e
                
    def TC_PopulateSubWin_old(self, tradeData):
        try:
            composeWindow = self.TC_ComposeWindow()
            field = "Create|Search..."
            control = self.ControlFromOR(composeWindow, field)       
            tc_control.SetField(control, tradeData['Create'][field]['Type'], tradeData['Create'][field]['Value'])
            subWindow = tc_control.WindowReady(self.pywin, "Find Equity")            
            for field in tradeData['SubWin']:
                control = self.ControlFromSubWinOR(subWindow, field)
                fieldData = tradeData['SubWin'][field]
                tc_control.SetField(control, fieldData['Type'], fieldData['Value'])
        except Exception, e:
            print e

    def TC_SetMainData(self, tradeData):
        try:
            composeWindow = self.TC_ComposeWindow()
            tabControl = composeWindow["&Message:TabControl"]
            currentTab = ""
            tradeData = csvTradeData(tradeData)
            for tab in tradeData.item(0):
                if tab != 'Create' and tab != 'SubWin'and tab != 'Overlay':
                    if tab != currentTab:
                        tc_control.WinTab_Select(tabControl, tab)
                        currentTab = tab
                    for field in tradeData.item(0)[tab]:
                        control = self.ControlFromOR(composeWindow, field)
                        tc_control.SetField(control, tradeData.item(0)[tab][field]['Type'], tradeData.item(0)[tab][field]['Value'])
        except Exception, e:
            print e

    def TC_CreateNewDeal(self, receiver, Cpty, trade_data, modifyData=""):
        try:
            mainWindow = self.TC_MainWindow()
            if not tc_control.WinMenu_Set(mainWindow, "&Deal->New Direct Deal...*"):
                tc_control.WinMenu_Set2(mainWindow, "^N")
            #tc_control.WinMenu_AutoItSet(self.main_win_title, "Deal->New Direct Deal...")
            
            composeWindow = self.TC_ComposeWindow()
            # Set the addresses for the user
            self.TC_SelectAddresses(receiver, composeWindow)
            
            # Set the data in the Create screen of the trade
            self.TC_SetCreateData(composeWindow, trade_data)
            
            tc_control.WinMenu_Set(composeWindow, "&Go->&Next")
            
            # Set the data in the main screen of the trade
            self.TC_SetMainData(trade_data)
            Cpty = self.receivers[receiver].get_property("le_name")
            print "Cpty", Cpty                          
            We = self.user.get_property("le_name")
            print "We",We
            counterpartyA = "Main|Counterparty A|combobox:={0}".format(Cpty)
            myEntityA = "Main|My Entity A|combobox:={0}".format(We)
            self.TC_AddDataHandler(counterpartyA+";"+myEntityA)
            tc_control.WinMenu_Set(composeWindow, "&Deal->&Affirm")
            tc_control.WinTab_Select(mainWindow["Template:TabControl"], "Internal Data")
            
            # Get the trade ID from the deal details section
            tradeId = tc_control.WinEdit_Get(self.ControlFromOR(mainWindow, "Internal Data|Private Deal ID"))
            tradeId = tradeId.split("/")[0]
            return tradeId
        except Exception, e:
            print e

    def TC_BiAmend(self, receiver, dealId, amendmentType, modifyData):
        try:
            self.TC_GoToDeal(user, dealId)
            mainWindow = self.TC_MainWindow()
            tc_control.WinMenu_Set(mainWindow, "&Deal->&Update->&Bilateral Amend")
            tc_control.WinComboBox_Set(self.pywin["Amendment"]["Amendment Type:ComboBox"], amendmentType)
            tc_control.WinButton_Click(self.pywin["Amendment"]["Continue"])
            title = self.TC_ComposeAmendmentTitle(user)
            self.TC_SelectAddresses(user, receiver, title, skipParticipant=True)
            self.TC_AddDataHandler(user, title, modifyData)
            composeWindow = self.TC_ComposeAmendmentWindow(user)
            tc_control.WinMenu_Set(composeWindow, "&Deal->&Affirm")
        except Exception, e:
            print e
        
    def TC_UniAmend(self, modifyField="InternalTradeID", modifyData="" , dealId=None):
        try:
            menuOptions = {'InternalTradeID':({tc_control.WinEdit_Set:'name=Internal Trade ID:Edit'},),
                       'SalesCredit':({tc_control.WinEdit_Set:'name=Sales Credit:Edit2'},)
                       }
            if dealId != None: print "dealid is:",dealId #self.TC_GoToDeal(dealId)
            mainWindow = self.TC_MainWindow()
            tc_control.WinMenu_Set(mainWindow, "&Deal->&Update->&Unilateral Amend")
            composeWindow = self.TC_ComposeUniAmendmentWindow()
            if modifyField in menuOptions:
                for proc in menuOptions[modifyField]:
                    for func,para in proc.items():
                        control = tc_control.GetProductControl(composeWindow, para)
                        func(control,modifyData)                
            tc_control.WinMenu_Set(composeWindow, "&Deal->&Save/Close")
            popupTexts = ["You are trying to access/update a deal with a book that you do not have permission for",
                        ]
            if tc_control.CheckMWPopup(self.pywin):
                for text in popupTexts:
                    tc_control.HandleMWPopUp(self.pywin,text)
                    tc_control.WindowClose(composeWindow)
                return False
            else:
                return True
        except Exception, e:
            print e
                    
    def TC_GoToDeal(self, dealId):
        try:
            mainWindow = self.TC_MainWindow()
            tc_control.WinMenu_Set(mainWindow, "&Deal->&Go To...")
            windowGoto = tc_control.WindowReady(self.pywin, "Go To Deal")
            tc_control.WinEdit_Set(windowGoto["&Trade ID:Edit"], dealId)        
            #tc_control.WinButton_Click(windowGoto["OK"])        
            tc_control.WinButton_AutoItClick("Go To Deal", "OK")
        except Exception, e:
            print e

    def TC_Pickup(self, dealId=None):
        try:
            mainWindow = self.TC_MainWindow()
            #tc_control.WinMenu_Set2(mainWindow, "%D+K")
            if not tc_control.WinMenu_Set(mainWindow, "&Deal->Pic&k Up")        :
                if not tc_control.WinMenu_Set2(mainWindow, "^K"):
                    return False
                else:
                    return True
                #LogMessage("TC_Affirm, affirmed the deal ")
            else:
                return True
        except Exception, e:
            print "TC_Pickup error:{0}".format(traceback.format_exc())
            return False

            
    def TC_Pull(self, dealId=None):
        try:
            mainWindow = self.TC_MainWindow()
            #tc_control.WinMenu_Set(mainWindow, "&Deal->P&ull Deal")
            if tc_control.WinMenu_Set2(mainWindow, "%D+U"):
                return True
            else:
                return False
        except Exception, e:
            print e
            return False


    def TC_Affirm(self, dealId=None):
        try:            
            mainWindow = self.TC_MainWindow()
            #if tc_control.WinMenu_Set2(mainWindow, "%D+I"):
            if not tc_control.WinMenu_Set(mainWindow, "&Deal->Affirm"):
                if not tc_control.WinMenu_Set2(mainWindow, "F7"):
                    return False
                else:
                    return True
                #LogMessage("TC_Affirm, affirmed the deal ")
            else:
                return True
                #LogMessage("TC_Affirm, could not affirm the deal ")
        except Exception, e:
            print e
            #LogMessage("TC_Affirm, could not affirm the deal " + e)
            return False

        
    def TC_AcceptAffirm(self, dealId=None):
        try:            
            mainWindow = self.TC_MainWindow()
            if not tc_control.WinMenu_Set(mainWindow, "&Deal->Accept/Affirm"):
                if not tc_control.WinMenu_Set2(mainWindow, "F9"):
                    return False
                else:
                    return True
                #LogMessage("TC_Affirm, affirmed the deal ")
            else:
                return True
                #LogMessage("TC_Affirm, could not affirm the deal ")
        except Exception, e:
            print e
            #LogMessage("TC_Affirm, could not affirm the deal " + e)
            return False


    def TC_Accept(self, dealId=None):
        try:            
            mainWindow = self.TC_MainWindow()
            if tc_control.WinMenu_Set(mainWindow, "&Deal->Accept"):
                return True
                #LogMessage("TC_Affirm, accepted the deal ")
            else:
                return False
                #LogMessage("TC_Affirm, could not accept the deal ")
        except Exception, e:
            print e
            #LogMessage("TC_Affirm, could not accept the deal " + e)
            return False


    def TC_DealDetails(self, dealId=None):
        try:
            mainWindow = self.TC_MainWindow()
            return tc_control.WinMenu_Tick(mainWindow, "&View->&Deal Details")
        except Exception, e:
            print e
            return False

    def TC_CheckDealDetails():
        try:
            mainWindow = self.TC_MainWindow()
            return tc_control.WinMenu_TickCheck(mainWindow, "&View->&Deal Details")
        except Exception, e:
            print e
            return False

    def TC_Transfer(self, dealId=None):
        try:
            mainWindow = self.TC_MainWindow()
            tc_control.WinMenu_Set(mainWindow, "&Deal->Transfer")
        except Exception, e:
            print e
            return False


    def TC_Release(self, dealId=None):
        try:
            #self.TC_GoToDeal(user, dealId)
            mainWindow = self.TC_MainWindow()
            #if tc_control.WinMenu_Set2(mainWindow, "%D+L"):
            if not tc_control.WinMenu_Set(mainWindow, "&Deal->Re&lease"):
                if not tc_control.WinMenu_Set2(mainWindow, "^L"):
                    return False
                else:
                    return True
                #LogMessage("TC_Affirm, affirmed the deal ")
            else:
                return True
                #LogMessage("TC_Release, could not release the deal ")
        except Exception, e:
            print e
            #LogMessage("TC_Release, could not release the deal " + e)
            return False


    def TC_Logout(self):
        try:
            mainWindow = self.TC_MainWindow()
            #tc_control.WinMenu_Set(mainWindow, "&File->&Logout")
            #tc_control.WinMenu_Set(mainWindow, "&File&->E&xit")
            result = tc_control.WinMenu_Set(mainWindow, "&File->&Logout")
            tc_control.WinMenu_Set(mainWindow, "&File&->E&xit")          
        except Exception, e:
            print e
        
        
    def TC_CheckDeal(self, dealId, dealData):
        try:
            self.TC_GoToDeal(user, dealId)
            
            mainWindow = self.TC_MainWindow()
            tabControl = mainWindow["Template:TabControl"]
            
            currentTab = ""
            for item in dealData.split(";"):
                field = item.split(":=")[0]
                value = item.split(":=")[1]
                
                aField = field.split("|")
                fieldTab = aField[0]
                fieldName = aField[0] + "|" + aField[1]
                fieldType = aField[2]
                
                if fieldTab != currentTab:
                    tc_control.WinTab_Select(tabControl, fieldTab)
                        
                    currentTab = fieldTab
                control = self.ControlFromOR(mainWindow, fieldName)
                actualValue = tc_control.GetField(control, fieldType)
                
                if tc_control.compareField(value, actualValue):
                    tc_control.LogMessage("Value matches: expected = " + value + " actual " + actualValue)
                else:
                    raise Exception("Value doesn't match: expected = " + value + " actual = " + actualValue)
        except Exception, e:
            print e

        
    def TC_GetFieldValue(self, fieldTab, fieldName, fieldType):
        try:
            mainWindow = self.TC_MainWindow()
            tabControl = mainWindow["Template:TabControl"]
            
            tc_control.WinTab_Select(tabControl, fieldTab)
            control = self.ControlFromOR(mainWindow, fieldTab + "|" + fieldName)
            return tc_control.GetField(control, fieldType)
        except Exception, e:
            print e
        
    def TC_SelectFolder(self, folder):
        # need to work out this doesn't always work
        #tc_control.WinMenu_Set(self.TC_MainWindow(), self.folders[folder][0])
        # this one uses kb shortcuts, but is a bit prone to menus changing
        #changed as per the above comment, if menu is not selected by the value only  in then case selct by shortcut
        try:
            if not tc_control.WinMenu_Set(self.TC_MainWindow(), self.folders[folder][0]):
                tc_control.WinMenu_Set2(self.TC_MainWindow(), self.folders[folder][1])
        except Exception, e:
            print e
            

    def TCSearch_Combo1Edit4(self, searchWindow, criteria):
        # Set a search field which consists of a ComboBox and an edit box
        try:
            menuOptions = {
                'Book ID':({tc_control.WinComboBox_Set:'name=isComboBox'},),
                'Trade Date':({tc_control.WinComboBox_Set:'name=ComboBox2'},
                              {tc_control.WinComboEdit_Set:'name=ComboBox6'}),
                'Trade ID':({tc_control.WinComboBox_Set:'name=App ID Option:ComboBox'},
                            {tc_control.WinComboEdit_Set:'name=App ID Option:Edit4'}),
                'Contract State':({tc_control.WinMultiComboBox_Check:'name=ComboBox6'},),
                'Booking State':({tc_control.WinComboBox_Set:'name=ComboBox6'},
                                 {tc_control.WinEdit_Set:'name=Booking State:Edit'}),
                'Activity Date':({tc_control.WinComboBox_Set:'name=ComboBox2'},
                                 {tc_control.WinComboEdit_Set:'window id=102'},
                                 {tc_control.WinComboEdit_Set:'name=toComboBox'})
                }
            control = tc_control.GetProductControl(searchWindow, 'name=-')
            if control.IsEnabled():
                control = tc_control.GetProductControl(searchWindow, 'name=ComboBox5')
                tc_control.WinComboBox_Set(control, criteria[0])
            else:
                control = tc_control.GetProductControl(searchWindow, 'name=ComboBox')
                tc_control.WinComboBox_Set(control, criteria[0])            
            option = tc_control.WinComboBox_Get(control)
            iCount = 1
            if option in menuOptions:
                for proc in menuOptions[option]:
                    for func,para in proc.items():
                        control = tc_control.GetProductControl(searchWindow, para)
                        func(control,criteria[iCount])
                        if iCount == len(criteria): break
                        iCount += 1
        except Exception, e:
            print e

        
    def TC_Search(self, search, expectedResult=''):
        try:
            """Do a deal search"""
            tc_control.WinMenu_Set(self.TC_MainWindow(), "&Deal->Search...")
            control = tc_control.GetProductControl(searchWindow, 'name=-Button')
              
            searchWindow = tc_control.WindowReady(self.pywin, "Search")
            criteria = search.split('|')
            self.TCSearch_Combo1Edit4(searchWindow, criteria)
            tc_control.WinButton_Click(searchWindow["OK"])
        except Exception, e:
            print e

    def TC_SearchMultipleCriteria(self, search, expectedResult=''):
        try:
            """Do a deal search"""
            tc_control.WinMenu_Set(self.TC_MainWindow(), "&Deal->Search...")
            searchWindow = tc_control.WindowReady(self.pywin, "Search")
            control = tc_control.GetProductControl(searchWindow, 'name=-')        
            while control.IsEnabled():
                tc_control.WinButton_Click(control)        
            control = tc_control.GetProductControl(searchWindow, 'name=+')
            i = 0
            for each_search in search:
                criteria = each_search.split('|')
                searchWindow = tc_control.WindowReady(self.pywin, "Search")
                if i >0 and i< len(search):
                    tc_control.WinButton_Click(control)            
                self.TCSearch_Combo1Edit4(searchWindow, criteria)
                i += 1
            tc_control.WinButton_Click(searchWindow["OK"])
            tc_control.HandleMWPopUp(self.pywin,"No results for given search criteria")
        except Exception, e:
            print e

        
    def TC_CheckBlotterData(self, search, check):
        try:
            checkColumns = ""
            for c in check.split(";"):
                checkColumns += c.split("=")[0] + ";"
            checkColumns = checkColumns[:-1]
            
            #tc_control.LogMessage("Start to get grid data")
            blotterData = tc_control.WinListView_GetGridData(self.TC_MainWindow()["ListView1"], checkColumns)
            #tc_control.LogMessage("Got grid data")
            
            bFound = False
            for row in range(0, len(blotterData)):
                bFound = True
                
                for c in check.split(";"):
                    field = c.split("=")[0]
                    value = c.split("=")[1];
                    bFound = bFound & (blotterData[row][field] == value)
                
                if bFound:
                    tc_control.LogMessage("Found " + check + " at " + str(blotterData[row]))
                    break
            
            if not bFound:
                raise Exception("Did not find " + check + " in the blotter")

            return len(blotterData)
        except Exception, e:
            print e


    def TC_GetBlotterData(self, search, check):
        try:
            self.TC_Search(search)
            
            checkColumns = ""
            for c in check.split(";"):
                checkColumns += c.split("=")[0] + ";"
            checkColumns = checkColumns[:-1]
            
            blotterData = tc_control.WinListView_GetGridData(self.TC_MainWindow()["ListView1"], checkColumns)
            
            return blotterData
        except Exception , e:
            print e

    def TC_SelectBlotterData(self, select):
        try:
            #tc_control.LogMessage("Start selecting " + select)
            
            checkColumns = ""
            for c in select.split(";"):
                checkColumns += c.split("=")[0] + ";"
                
            checkColumns = checkColumns[:-1]
            
            blotterData = tc_control.WinListView_GetGridData(self.TC_MainWindow()["ListView1"], checkColumns)
            
            bFound = False
            for row in range(0, len(blotterData)):
                bFound = True
                
                #print blotterData[row]
                for c in select.split(";"):
                    field = c.split("=")[0]
                    value = c.split("=")[1];
                    bFound = bFound & (blotterData[row][field] == value)
                
                if bFound:
                    #tc_control.LogMessage("Found " + select + " at " + str(blotterData[row]))
                    #tc_control.LogMessage("Select row " + str(row))
                    self.TC_MainWindow()["ListView1"].Select(row)
                    #tc_control.LogMessage("Finished selecting row " + str(row))
                    break
            
            if not bFound:
                raise Exception("Did not find " + select + " in the blotter")
            return len(blotterData)
        except Exception, e:
            print e


    def TC_GetBlotterData2(self, select):
        """Get all contents of blotter for selected fields"""
        try:
            checkColumns = ""
            for c in select.split(";"):
                checkColumns += c.split("=")[0] + ";"
            checkColumns = checkColumns[:-1]

            #tc_control.LogMessage("Start selecting " + select)
            blotterData = tc_control.WinListView_GetGridData(self.TC_MainWindow()["ListView1"], checkColumns)
            return blotterData
        except Exception, e:
            print e

    def TC_SelectBlotterLine(self, row):
        try:
            """Select a single item line in blotter"""
            mainWin = self.TC_MainWindow()
            #tc_control.ControlReady(mainWin["ListView1"])
            mainWin["ListView1"].Select(row)
        except Exception, e:
            print e

    def TC_DeselectBlotterLine(self, row):
        try:
            """De-Select a single item line in blotter"""
            mainWin = self.TC_MainWindow()
            #tc_control.ControlReady(mainWin["ListView1"])
            mainWin["ListView1"].Deselect(row)
        except Exception, e:
            print e

    def TC_GetSelectedBlotterLineCount(self):
        try:
            """returns the number of selcted deals in blotterline"""
            mainWin = self.TC_MainWindow()
            #tc_control.ControlReady(mainWin["ListView1"])
            return mainWin["ListView1"].GetSelectedCount()
        except Exception, e:
            print e

    def TC_CheckBlotterLineSelected(self, row):
        try:
            """check if a specified deal is selected in blotterline"""
            mainWin = self.TC_MainWindow()
            #tc_control.ControlReady(mainWin["ListView1"])
            if mainWin["ListView1"].IsSelected(row):
                return True
            else:
                return False
        except Exception, e:
            print e			

    def TC_GetBlotterLineCount(self):
        try:
            """Returns the number of deals in blotter line"""
            mainWin = self.TC_MainWindow()
            #tc_control.ControlReady(mainWin["ListView1"]) 
            return mainWin["ListView1"].ItemCount()
        except Exception, e:
            print e

    def TC_WinListViewScroll(self):
        #scroll list view, just for testing.. not working and need changes
        tc_control.WinListView_Scroll(self.TC_MainWindow()["ListView1"])

    def TC_SelectBlotterDataList(self, select, values):
        try:
            # select from a list of values for a single field 
            #(to allow for trade ids varying for novations depending on whether displayed yet)
            #tc_control.LogMessage("Start selecting " + select)
            
            checkColumns = ""
            for c in select.split(";"):
                checkColumns += c.split("=")[0] + ";"
                
            checkColumns = checkColumns[:-1]
            
            blotterData = tc_control.WinListView_GetGridData(self.TC_MainWindow()["ListView1"], checkColumns)
            
            bFound = False
            for row in range(0, len(blotterData)):
                bFound = True
                for c in select.split(";"):
                    field = c.split("=")[0]
                    bFound = bFound & (blotterData[row][field] in values)
                if bFound:
                    self.TC_MainWindow()["ListView1"].Select(row)
                    break            
            if not bFound:
                raise Exception("Did not find " + select + str(values) + " in the blotter")
            return len(blotterData)
        except Exception, e:
            print e

    def TC_Action(self,action):
        try:
            actions = {
                'Pickup': self.TC_Pickup,
                'Affirm': self.TC_Affirm,
                'Release': self.TC_Release,
                'AcceptAffirm': self.TC_AcceptAffirm,
                'Uniamend':self.TC_UniAmend
                }
            if action in actions:
                result = actions[action](self)
            return result
        except Exception, e:
            print "TC_Action error:{0}".format(traceback.format_exc())
            #tc_control.LogMessage(e)

    def TC_ActionAvailable(self, action):
        try:
            mainWindow = self.TC_MainWindow()
            menuItems={"Pickup": "&Deal->Pic&k Up",
                       "Affirm": "&Deal->Affirm",
                       "AcceptAffirm": "&Deal->Accept/Affirm",
                       "Release": "&Deal->Re&lease",
                       "Uniamend": "&Deal->&Update->&Unilateral Amend"
                       }
            if action in menuItems:
                result = tc_control.WinMenu_Check(mainWindow, menuItems[action])
            return result
        except Exception, e:
            print e
            #tc_control.LogMessage(e)
            
            