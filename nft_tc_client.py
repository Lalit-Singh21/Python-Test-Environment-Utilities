#!/usr/bin/env python
"""actions for NFT"""

import os
import platform
import subprocess
import time
import collections
from nft_util import NFTLoginit, NFTMemory
import tc_control
import tc_function

class MWSession():

    def __init__(self):
        self.custom_timers = {}  # transaction timings
        self.transactions = {}   # working dict for transactions
        self.config = {}         # user config details
        self.output_dir = ""     # output dir for logging
        
    def login(self):
        username = self.config['username']
        try:
            db = self.config_main['ora_db']
        except:
            db = "NFT21MSV"
        if 'host' not in self.config: self.config['host'] = os.environ['SW_UNIT_TEST_HOST']
        self.logger = NFTLoginit(server=self.config['host'].replace(":","-")
                               , user=self.config['username'], dir=self.output_dir)
        self.loginfo(self.config)

        self.trans_start('Login')
        tc_version = self.config['build']
        x = tc_version.split("_")
        ver_num = float(x[1] + "." + x[2][0])
        self.trade_str = "Trade ID - Private Deal ID" if ver_num > 10.1 else "Trade ID"
        self.config['release'] = platform.release()
        tc_path = os.path.join(os.environ["TC_CLIENT"], "\\".join([tc_version, "tc_client.exe"]))
        self.config["tc_path"] = tc_path
        self.disconnect()
        print "self.output_dir: ",self.output_dir
        self.tc_session = tc_function.TCSession(self.output_dir, db,
                                                tc_path, host=self.config['host'])
        self.tc_session.TC_Login(username)
        self.trans_end('Login', "server=%s" % self.config['host'])

    def disconnect(self):
        subprocess.call(["pskill", "tc_client"])

    def logout(self):
        self.trans_start('Logout')
        self.tc_session.TC_Logout()
        self.trans_end('Logout', "server=%s" % self.config['host'])

    def TC_ProcessActive(self,skipAffirm=0):
        """ Progress all active deals through happy path
            So pickup, affirm, release as required
            Similar to nft_session_base.MWProcessActive
        """
        num_of_retry = 0
        actions_on_trades = 0      
        self.process = {'All':{'Direct':("Pickup",),
                               'Active': ("AcceptAffirm", "Affirm", "Release"),
                               'Brokered': ("Pickup",),
                               'Novations': ("Pickup", "Affirm", "Release")}}
     
        for proc in self.process:
            try:
                for folder in self.process[proc]:
                    continueFolder = True
                    self.loginfo("Starting Folder={0}".format(folder))
                    self.tc_session.TC_SelectFolder(folder)
                    position = 0
                    #selecting each trade to process actions
                    while continueFolder:
                        if position >= len(self.tc_session.TC_GetBlotterData2(self.trade_str)):
                            continueFolder = False
                            break
                        #ensure blotter has no selected deal
                        for action in self.process[proc][folder]:
                            if (skipAffirm and folder == "Active" and action == "Affirm"):
                                continue
                            self.loginfo("Starting folder={0}, action={1}, pos={2}".format(folder,action,position))
                            self.tc_session.TC_SelectFolder(folder)
                            self.TC_Cleardealselection()
                            self.tc_session.TC_SelectBlotterLine(position)
                            trade=self.tc_session.TC_GetBlotterData2(self.trade_str)[position]
                            tid = trade.values()[0].split('/')                           
                            if self.tc_session.TC_ActionAvailable(action):
                                self.loginfo("action available : {0}, tid={1}".format(action,tid[0]))
                                if folder == "Active":
                                    self.tc_session.TC_SelectFolder("Exercise")
                                    self.tc_session.TC_SelectFolder(folder)                                
                                    self.tc_session.TC_SelectBlotterLine(position)
                                self.trans_start("TC_{0}".format(action))                                
                                if self.tc_session.TC_Action(action):
                                    self.loginfo("action done : {0}, tid={1}".format(action,tid[0]))
                                    self.trans_end("TC_{0}".format(action),"tid={0}".format(tid[0]))
                                    actions_on_trades += 1
                                else:
                                   self.logerror("failed processing action :{0} for trade:{1}".format(action,tid[0]))
                            else:
                                self.loginfo("action not available : {0}, tid={1}".format(action,tid[0]))

                        temp=[]
                        self.tc_session.TC_SelectFolder(folder)
                        trades = self.tc_session.TC_GetBlotterData2(self.trade_str)
                        for x in trades:
                            temp.extend(x.values())
                        if [element for element in temp if isinstance(element, collections.Iterable) and (tid[0] in element)]:
                            position += 1                          
                        del temp[:]
            except tc_control.WindowNotFoundError:
                num_of_retry += 1
                if num_of_retry < 5:
                    continue
                else:
                    raise tc_control.WindowNotFoundError
            except Exception:
                    raise
                    
        return actions_on_trades



    def TC_Cleardealselection(self):
            if self.tc_session.TC_GetSelectedBlotterLineCount() > 0 :
                for selected_deal in range (0,len(self.tc_session.TC_GetBlotterData2(self.trade_str))-1):
                    if self.tc_session.TC_CheckBlotterLineSelected(selected_deal):
                        self.tc_session.TC_DeselectBlotterLine(selected_deal)
                        if self.tc_session.TC_GetSelectedBlotterLineCount() == 0 : break

    def TC_SelectDealonPosition(self,position):
        for selected_deal in range (0,len(self.tc_session.TC_GetBlotterData2(self.trade_str))-1):
            if position == selected_deal:
                self.tc_session.TC_SelectBlotterLine(position)                                
                continue
            else:
                self.tc_session.TC_DeselectBlotterLine(selected_deal)
                if self.tc_session.TC_GetSelectedBlotterLineCount() == 1 : break


    def TC_SearchDeals_getDetails(self,activity_date_from,search_string="",trades_to_select=0):
        """
        search deals based on the given criteria
        1) activity date|is in the range| from mm/dd/yyyy-to mm/dd/yyyy/
        2) other customized criteria eg; Booking State|is|Released
        3) number of result deals to be selected and display deals menu item is clicked
        """
        mainWindow = self.tc_session.TC_MainWindow()
        activity_date_to = ""
        if activity_date_from == "":
            activity_date_to = time.strftime("%Y-%m-%d",time.localtime(self.test_start_time))
        self.search = ["Activity Date|is in the range|{0}|{1}".format(activity_date_from,activity_date_to),
                     "{0}".format(search_string)]
        self.search = filter(None, self.search)
        self.trans_start('TC_Search')
        self.tc_session.TC_SearchMultipleCriteria(self.search)
        self.trans_end('TC_Search', "search={0}".format(self.search))
        trades = self.tc_session.TC_GetBlotterData2(self.trade_str)
        self.loginfo("Number of trades searched : {0}".format(len(trades)))
        if trades_to_select>0:            
            position = 0
            self.tc_session.TC_DealDetails()           
            for trade in trades:
                self.trans_start('TC_Select&DealDetails')
                self.tc_session.TC_SelectBlotterLine(position)
                tc_control.WinTab_Select(mainWindow["Template:TabControl"], "Internal Data")
                # Get the trade ID from the deal details section
                tradeId = tc_control.WinEdit_Get(self.tc_session.ControlFromOR(mainWindow, "Internal Data|Private Deal ID"))
                if self.tc_session.TC_CheckDealDetails:
                    tradeId = tradeId.split("/")[0]
                    self.trans_end('TC_Select&DealDetails',"tid={0}".format(tradeId))
                else:
                    self.logerror("Trade is not displayed : {0}".format(tradeId))
                self.tc_session.TC_DeselectBlotterLine(position)
                position += 1
                if position == trades_to_select: break
        return len(trades)        
        
    def TC_UpdateDeals(self,activity_date_from,search_string="",trades_to_update=0):
        """
        search deals as per TC_SearchDeals_getDetails, and update each deals
        PrivateTradeId to time.strftime("%Y%m%d-%H%M%S").
        """
        mainWindow = self.tc_session.TC_MainWindow()
        len_trades = self.TC_SearchDeals_getDetails(activity_date_from,search_string)
        trades = self.tc_session.TC_GetBlotterData2(self.trade_str)
        position = 0
        self.tc_session.TC_DealDetails()
        for trade in trades:
            if self.tc_session.TC_GetSelectedBlotterLineCount() > 0 :
                for selected_deal in range (0,len(trades)-1):
                    if self.tc_session.TC_CheckBlotterLineSelected(selected_deal):
                        self.tc_session.TC_DeselectBlotterLine(selected_deal)
                        if self.tc_session.TC_GetSelectedBlotterLineCount() == 0 : break            
            self.tc_session.TC_SelectBlotterLine(position)
            tc_control.WinTab_Select(mainWindow["Template:TabControl"], "Internal Data")
            # Get the trade ID from the deal details section
            tradeId = tc_control.WinEdit_Get(self.tc_session.ControlFromOR(mainWindow, "Internal Data|Private Deal ID"))                  
            #update private trade id
            if self.tc_session.TC_ActionAvailable("Uniamend"):
                self.trans_start("TC_Uniamend")
                action = self.tc_session.TC_UniAmend("InternalTradeID",time.strftime("%Y%m%d-%H%M%S",time.localtime(self.test_start_time)))
                if action == True :
                    tradeId = tradeId.split("/")[0]
                    self.trans_end("TC_Uniamend","tid={0}".format(tradeId))
                else:
                    self.logerror("Trade could not be uniamended : {0}".format(tradeId))
                position += 1
                if position == trades_to_update: break
        return len(trades)

    def TC_CreateDirectDeals(self,receiver,receiver_LE,trade_data):
        """
        Create TC direct deal
        """
        self.trans_start("TC_CreateDirectDeal", "file="+trade_data)
        tradeId = self.tc_session.TC_CreateNewDeal(receiver,receiver_LE,trade_data)
        self.trans_end("TC_CreateDirectDeal","tid={0}".format(tradeId)) if tradeId != None and tradeId != "" else self.logerror("Trade could not be submitted : {0}".format(tradeId))


    def TC_BrowseFolders(self):
        """ display deal from each folders, Direct,Brokered, Active and Novation
        """
        num_of_retry = 0
        num_trades_selected = 0      
        self.folders = ['Direct','Active','Brokered','Novations']
        mainWindow = self.tc_session.TC_MainWindow()
        
        for folder in self.folders:
            try:            
                continueFolder = True
                self.loginfo("Starting Folder={0}".format(folder))
                self.tc_session.TC_SelectFolder(folder)
                position = 0
                self.tc_session.TC_DealDetails()
                #selecting each trade to process actions
                while continueFolder:
                    if position >= len(self.tc_session.TC_GetBlotterData2(self.trade_str)):
                        continueFolder = False
                        break
                    #ensure blotter has no selected deal
                    self.TC_Cleardealselection()
                    self.trans_start("TC_{0}".format(folder))
                    self.tc_session.TC_SelectBlotterLine(position)
                    tc_control.WinTab_Select(mainWindow["Template:TabControl"], "Internal Data")
                    trade=self.tc_session.TC_GetBlotterData2(self.trade_str)[position]
                    tid = trade.values()[0].split('/')                           
                    self.loginfo("Deal selected in folder : {0}, tid={1}".format(folder,tid[0]))
                    self.trans_end("TC_{0}".format(folder),"tid={0}".format(tid[0]))
                    self.tc_session.TC_DeselectBlotterLine(position)                    
                    position += 1
                    num_trades_selected += 1
                
            except Exception:
                    raise
                    
        return num_trades_selected

  
    def loginfo(self, logmsg):
        self.logger.info("%s|%s" % (self.config['username'],logmsg))

    def logerror(self, logmsg):
        self.logger.error("%s|%s" % (self.config['username'],logmsg))

    def logwarning(self, logmsg):
        self.logger.warning("%s|%s" % (self.config['username'],logmsg))

    def trans_start(self, name, logtext=""):
        # store start time and memory
        mem = NFTMemory()
        self.transactions[name] = [ time.time(), mem ]
        self.loginfo('trans_start|%s||memtot=%s,%s' % (name, mem, logtext))

    def trans_end(self, name, logtext=""):
        # store and output latency and memory used
        mem = NFTMemory()
        latency = time.time() - self.transactions[name][0]
        memused = mem - self.transactions[name][1]
        self.custom_timers[name] = latency
        self.loginfo('trans_end|%s|%f|memtot=%s,memused=%s,%s' %
                                        (name, latency, mem, memused, logtext))
