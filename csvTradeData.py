import collections

class csvTradeData:
    tabRow   = 0
    labelRow = 1
    typeRow  = 2
    tradeData = collections.OrderedDict()
    
    def __init__(self, filename):
        i = 0
        
        f = open(filename, "r")
        line = f.readline()
        line = line.rstrip()
        aTabRow   = line.split("\t")
        
        line = f.readline()
        line = line.rstrip()
        aLabelRow = line.split("\t")
        
        line = f.readline()
        line = line.rstrip()
        aTypeRow  = line.split("\t")
        
        for line in f:
            line = line.rstrip()

            row = line.split("\t")
    
            for col in range(1, len(row)):
                tab   = aTabRow[col]
                
                if tab != '' and row[col] != '':
                    field = aLabelRow[col]
                    fieldType  = aTypeRow[col]
                    key   = tab + "|" + field
                    
                    if not i in self.tradeData:
                        self.tradeData[i] = collections.OrderedDict()
                                            
                    if not tab in self.tradeData[i]:
                        self.tradeData[i][tab] = collections.OrderedDict()
                                            
                    if not key in self.tradeData[i][tab]:
                        self.tradeData[i][tab][key] = collections.OrderedDict()
                    
                    self.tradeData[i][tab][key]['Value'] = row[col]
                    self.tradeData[i][tab][key]['Type'] = fieldType
                     
                    #print key + "=" + self.tradeData[i][tab][key]['Value']
        f.close()
                    
    def tradeDataKeys(self):
        return self.tradeData.keys()

    def item(self, index):
        return self.tradeData[index]
        
    def overlayData(self, index):
        return self.tradeData[index]["Overlay"]
    
    def createData(self, index):
        return self.tradeData[index]["Create"]

    def subWinData(self, index):
        return self.tradeData[index]["SubWin"]
                
