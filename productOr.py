# object repository - this all needs looking at!

import os
from lxml import etree

doc = ''
nsQtpRep = {'qtpRep': 'http://www.mercury.com/qtp/ObjectRepository'}
subWinDoc = etree.parse(os.environ["NFT_TEST_DATA"] + r'\TC_trades\TraderClient_'+"EquityIndexOptionData"+r'_10_3.xml')


def SetData(data):
    global doc
    trade_data = os.path.basename(os.path.splitext(data)[0])
    doc = etree.parse(os.environ["NFT_TEST_DATA"] + r'\TC_trades\TraderClient_'+trade_data+r'_10_3.xml')


def controlWindowId(name):
    global doc
    if doc == '':
        doc = subWinDoc
    xPath = "//qtpRep:Object[@Name=\"" + name + "\"]/qtpRep:Properties/qtpRep:Property[@Name=\"window id\"]/qtpRep:Value"
    #print xPath

    controlWindowId = doc.xpath(xPath, namespaces = nsQtpRep)[0].text
                            
    #print "window id of " + name + " is " + controlWindowId
    
    return "window id=" + str(controlWindowId)

def subWinControlWindowId(name):
    try:
        xPath = "//qtpRep:Object[@Name=\"" + name + "\"]/qtpRep:Properties/qtpRep:Property[@Name=\"window id\"]/qtpRep:Value"
    
        controlWindowId = subWinDoc.xpath(xPath, namespaces = nsQtpRep)[0].text
        
        #print "window id of " + name + " is " + controlWindowId
        
        return "window id=" + str(controlWindowId)
    except IndexError:
        xPath = "//qtpRep:Object[@Name=\"" + name + "\"]/qtpRep:Properties/qtpRep:Property[@Name=\"text\"]/qtpRep:Value"
    
        controlWindowId = subWinDoc.xpath(xPath, namespaces = nsQtpRep)[0].text
        
        #print "text attribute of " + name + " is " + controlWindowId
        
        return "text=" + str(controlWindowId)
    
    
