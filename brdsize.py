#!/cygdrive/c/Python37/Python.exe
#!/usr/local/bin/python2.7

import wx
import os
import re
import platform
import time
from time import strftime,localtime
from ezdxf import readfile as ReadFile
import sys
from sys import stdout

linux = platform.system() == 'Linux'

if linux:
    pass
else:
    pass

depth = -0.125

info = {}

class InfoValue():
    def __init__(self, val):
        self.value = val

    def GetValue(self):
        return(self.value)

    def SetValue(self, val):
        self.value = val

def saveInfo(file):
    global info
    f = open(file, 'w')
    for key in sorted(info.keys()):
        val = info[key]
        valClass = val.__class__.__name__
        # print(key, valClass)
        # stdout.flush()
        if valClass == 'TextCtrl':
            f.write("%s=%s\n" % (key, val.GetValue()))
        elif valClass == 'RadioButton':
            f.write("%s=%s\n" % (key, val.GetValue()))
        elif valClass == 'CheckBox':
            f.write("%s=%s\n" % (key, val.GetValue()))
        elif valClass == 'InfoValue':
            f.write("%s=%s\n" % (key, val.GetValue()))
        elif valClass == 'StaticText':
            pass
    f.close()

def readInfo(file):
    global info
    try:
        f = open(file, 'r')
        for line in f:
            line = line.rstrip()
            if len(line) == 0:
                continue
            (key, val) = line.split('=')
            if key in info:
                func = info[key]
                funcClass = func.__class__.__name__
                # print(key, val, funcClass)
                if funcClass == 'TextCtrl':
                    func.SetValue(val)
                elif funcClass == 'RadioButton':
                    if val == 'True':
                        func.SetValue(True)
                elif funcClass == 'CheckBox':
                    if val == 'True':
                        func.SetValue(True)
            else:
                # print(key, val)
                func = InfoValue(val)
                info[key] = func
            # stdout.flush()
        f.close()
    except Exception as e:
        print(line, "readInfo error")
        print(e)
        stdout.flush()

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title)
        if linux:
            self.dirname = '/home/eric/linuxcnc/nc_files'
        else:
            # self.dirname = 'c:/Development/Circuits/RS485/Test'
            self.dirname = 'c:/Development/Python/BoardSize/'
        self.Bind(wx.EVT_CLOSE,self.onClose)
        self.InitUI0()

    def onClose(self, event):
        self.Destroy()

    def addCheckBox(self, panel, sizer, label, key, action=None):
        txt = wx.StaticText(panel, -1, label)
        sizer.Add(txt, flag=wx.ALL|wx.ALIGN_RIGHT|\
                  wx.ALIGN_CENTER_VERTICAL, border=2)

        cb = wx.CheckBox(panel, -1, style=wx.ALIGN_LEFT)
        if action != None:
            self.Bind(wx.EVT_CHECKBOX, action, cb)
        sizer.Add(cb, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2)
        info[key] = cb
        return(cb)

    def InitUI0(self):
        global info
        panel = wx.Panel(self)

        self.sizerV = sizerV = wx.BoxSizer(wx.VERTICAL)

        #

        btn = wx.Button(panel, label='File')
        btn.Bind(wx.EVT_BUTTON, self.OnSelect)
        sizerV.Add(btn, flag=wx.CENTER|wx.ALL, border=2)

        #

        self.projectName = txt = wx.StaticText(panel, -1, "Select Project")
        sizerV.Add(txt, flag=wx.CENTER|wx.ALL, border=2)

        #

        sizerH = wx.BoxSizer(wx.HORIZONTAL)

        self.widthBtn = btn = wx.RadioButton(panel, label="Width",
                                        style = wx.RB_GROUP)
        sizerH.Add(btn, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        btn.Bind(wx.EVT_RADIOBUTTON, self.OnWidth)

        self.boardWidth = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        tc.SetEditable(False)
        sizerH.Add(tc, flag=wx.ALL, border=2)

        self.heightBtn = btn = wx.RadioButton(panel, label="Height")
        sizerH.Add(btn, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        btn.Bind(wx.EVT_RADIOBUTTON, self.OnHeight)

        self.boardHeight = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        tc.SetEditable(False)
        sizerH.Add(tc, flag=wx.ALL, border=2)

        sizerV.Add(sizerH, flag=wx.CENTER|wx.ALL, border=2)

        #

        # self.boardSize = txt = wx.StaticText(panel, -1, "")
        # sizerV.Add(txt, flag=wx.CENTER|wx.ALL, border=2)

        #

        sizerH = wx.BoxSizer(wx.HORIZONTAL)

        txt = wx.StaticText(panel, -1, "Feed")
        sizerH.Add(txt, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2)

        self.feed = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        sizerH.Add(tc, flag=wx.ALL, border=2)
        info['feed'] = tc

        self.climb = self.addCheckBox(panel, sizerH, "Climb", "climb")

        sizerV.Add(sizerH, flag=wx.CENTER|wx.ALL, border=2)

        #

        sizerH = wx.BoxSizer(wx.HORIZONTAL)

        txt = wx.StaticText(panel, -1, "Overhang")
        sizerH.Add(txt, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2)

        self.overHang = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        sizerH.Add(tc, flag=wx.ALL, border=2)
        info['overHang'] = tc

        txt = wx.StaticText(panel, -1, "X Clear")
        sizerH.Add(txt, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2)

        self.xClear = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        sizerH.Add(tc, flag=wx.ALL, border=2)
        info['xClear'] = tc

        sizerV.Add(sizerH, flag=wx.CENTER|wx.ALL, border=2)

        #

        sizerH = wx.BoxSizer(wx.HORIZONTAL)

        btn = wx.Button(panel, label='Cut Here')
        btn.Bind(wx.EVT_BUTTON, self.OnCutHere)
        sizerH.Add(btn, flag=wx.ALL, border=2)

        txt = wx.StaticText(panel, -1, "X Size")
        sizerH.Add(txt, flag=wx.CENTER|wx.ALL, border=2)

        self.widthBox = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        sizerH.Add(tc, flag=wx.ALL, border=2)
        info['widthBox'] = tc

        sizerV.Add(sizerH, flag=wx.CENTER|wx.ALL, border=2)

        #

        sizerH = wx.BoxSizer(wx.HORIZONTAL)

        txt = wx.StaticText(panel, -1, "Y Size")
        sizerH.Add(txt, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2)

        self.yBox = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        sizerH.Add(tc, flag=wx.ALL, border=2)
        info['yBox'] = tc

        txt = wx.StaticText(panel, -1, "Y Extra")
        sizerH.Add(txt, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2)

        self.yExtraBox = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        sizerH.Add(tc, flag=wx.ALL, border=2)
        info['yExtraBox'] = tc

        sizerV.Add(sizerH, flag=wx.CENTER|wx.ALL, border=2)

        #

        sizerH = wx.BoxSizer(wx.HORIZONTAL)

        btn = wx.Button(panel, label='Cut')
        btn.Bind(wx.EVT_BUTTON, self.OnCut)
        sizerH.Add(btn, flag=wx.ALL, border=2)

        txt = wx.StaticText(panel, -1, "Bit Dia")
        sizerH.Add(txt, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2)

        self.cutBitDia = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        sizerH.Add(tc, flag=wx.ALL, border=2)
        info['cutBitDia'] = tc

        sizerV.Add(sizerH, flag=wx.CENTER|wx.ALL, border=2)

        #

        sizerH = wx.BoxSizer(wx.HORIZONTAL)

        txt = wx.StaticText(panel, -1, "Ruler")
        sizerH.Add(txt, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2)

        self.rulerBox = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        # tc.SetEditable(False)
        sizerH.Add(tc, flag=wx.ALL, border=2)

        self.rulerTxt = txt = wx.StaticText(panel, -1, "")
        sizerH.Add(txt, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2)

        sizerV.Add(sizerH, flag=wx.CENTER|wx.ALL, border=2)

        #

        sizerH = wx.BoxSizer(wx.HORIZONTAL)

        txt = wx.StaticText(panel, -1, "Bit Dia")
        sizerH.Add(txt, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2)

        self.trimBitDia = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        sizerH.Add(tc, flag=wx.ALL, border=2)
        info['trimBitDia'] = tc

        txt = wx.StaticText(panel, -1, "Y Measurement")
        sizerH.Add(txt, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2)

        self.yRMeasureBox = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        sizerH.Add(tc, flag=wx.ALL, border=2)
        # info['yRMeasureBox'] = tc

        sizerV.Add(sizerH, flag=wx.CENTER|wx.ALL, border=2)

        #

        sizerH = wx.BoxSizer(wx.HORIZONTAL)

        btn = wx.Button(panel, label='Trim Rough')
        btn.Bind(wx.EVT_BUTTON, self.OnTrimRough)
        sizerH.Add(btn, flag=wx.ALL, border=2)

        sizerV.Add(sizerH, flag=wx.CENTER|wx.ALL, border=2)

        #

        sizerH = wx.BoxSizer(wx.HORIZONTAL)

        txt = wx.StaticText(panel, -1, "Y Loc")
        sizerH.Add(txt, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2)

        self.yLocBox = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        sizerH.Add(tc, flag=wx.ALL, border=2)
        info['yLocBox'] = tc

        txt = wx.StaticText(panel, -1, "Y Measurement")
        sizerH.Add(txt, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2)

        self.yMeasureBox = tc = wx.TextCtrl(panel, -1, "", size=(60, -1))
        sizerH.Add(tc, flag=wx.ALL, border=2)
        # info['yMeasureBox'] = tc

        sizerV.Add(sizerH, flag=wx.CENTER|wx.ALL, border=2)

        #

        sizerH = wx.BoxSizer(wx.HORIZONTAL)

        btn = wx.Button(panel, label='Trim Final')
        btn.Bind(wx.EVT_BUTTON, self.OnTrimFinal)
        sizerH.Add(btn, flag=wx.ALL, border=2)

        sizerV.Add(sizerH, flag=wx.CENTER|wx.ALL, border=2)

        #

        self.status = txt = wx.StaticText(panel, -1, "")
        sizerV.Add(txt, flag=wx.CENTER|wx.ALL, border=2)

        panel.SetSizer(sizerV)
        self.sizerV.Fit(self)

        dw, dh = wx.DisplaySize()
        w, h = self.GetSize()
        self.SetPosition((dw - w, 0))

        self.tmpPath = ""
        runDir = os.path.dirname(os.path.abspath(__file__))
        self.configFile = os.path.join(runDir, 'config.txt')
        readInfo(self.configFile)

    def readVal(self, box):
        result = 0.0
        val = box.GetValue()
        if len(val) != 0:
            try:
                result = float(val)
            except:
                self.error = True
        else:
            self.error = True
        return(result)

    def OnSelect(self,e):
        dlg = wx.FileDialog(self, "Choose a file", self.dirname,
                            "", "*.drl;*.dxf", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            # os.system(rm + '*.png')
            # self.yBox.SetValue("")
            # self.offsetBox.SetValue("")
            # self.inputBox.SetValue("")
            # self.status.SetLabel("")
            self.filename = filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            
            pattern = "cut\d[\w]*\.ngc"
            for f in os.listdir(self.dirname):
                if re.search(pattern, f):
                    os.remove(os.path.join(self.dirname, f))

            gbr = False
            dxf = False
            if re.search("\.drl$", filename):
                self.project = re.sub("\\.drl", "", filename)
                self.filename =  re.sub("\\.drl", ".gbr", filename)
                gbr = True
            elif re.search("\.dxf$", filename):
                self.project = re.sub("\\.drl", "", filename)
                self.filename =  re.sub("\\.drl", ".gbr", filename)
                dxf= True
                
            self.path = os.path.join(self.dirname, self.filename)

            if gbr:
                self.openGbr(self.path)
            if dxf:
                self.openDxf(self.path)
            
            # self.boardSize.SetLabel("%5.3f x %5.3f" %
            #                         (self.xSize, self.ySize))
            self.boardWidth.SetValue("%5.3f" % self.xSize)
            self.boardHeight.SetValue("%5.3f" % self.ySize)
            self.updateSize()
            self.projectName.SetLabel(self.project)
            self.sizerV.Layout()

    def openGbr(self, inFile):
        self.xSize = 0
        self.ySize = 0
        f = open(inFile, "r")
        for line in f:
            line = line.strip();
            while True:
                m = re.match("^([XY])([0-9]+)", line)
                if m == None:
                    break
                print(m.group(1), m.group(2))
                axis = m.group(1)
                val = int(m.group(2))
                if val > 100000:
                    val /= 1000000.0
                else:
                    val /= 10000.0
                if axis == "X":
                    if val > self.xSize:
                        self.xSize = val
                else:
                    if val > self.ySize:
                        self.ySize = val
                # print("len %d start %d end %d" % \
                #       (len(line), m.start(0), m.end(0)))
                line = line[m.end(0):]

    def openDxf(self, inFile):
        self.dwg = dwg = ReadFile(inFile)
        self.modelspace = modelspace = dwg.modelspace()
        xMin = 9999
        yMin = 9999
        xMax = -999
        yMax = -999
        for e in modelspace:
            type = e.dxftype()
            # print("type %s" % (type))
            # print(e.get_dxf_attrib("layer"))
            layer = e.get_dxf_attrib("layer")
            if type == 'LINE':
                if layer == 'Material':
                    (x0, y0, z0) = e.get_dxf_attrib("start")
                    (x1, y1, z1) = e.get_dxf_attrib("end")
                    xMin = min(x0, x1, xMin)
                    yMin = min(y0, y1, yMin)
                    xMax = max(x0, x1, xMax)
                    yMax = max(y0, y1, yMax)
                # print e.get_dxf_attrib("start")
                # print e.get_dxf_attrib("end")
                # print("LINE on layer: %s" % e.dxf.layer)
                # print("start point: %s" % e.dxf.start)
                # print("end point: %s" % e.dxf.end)
        self.xSize = xMax - xMin
        self.ySize = yMax - yMin
        print("xSize %5.3f ySize %6.3f" % (self.xSize, self.ySize))


    def updateSize(self):
        if self.widthBtn.GetValue():
            val = self.boardWidth.GetValue()
            width = self.boardHeight.GetValue()
        else:
            val = self.boardHeight.GetValue()
            width = self.boardWidth.GetValue()
        self.yBox.SetValue(val)
        self.widthBox.SetValue(width)
        boardSize = float(val)
        extra = float(self.yExtraBox.GetValue())
        self.yRMeasureBox.SetValue("%5.3f" % (boardSize + extra))
        self.yMeasureBox.SetValue("%5.3f" % (boardSize + extra / 2))

    def OnWidth(self, e):
        self.updateSize()

    def OnHeight(self, e):
        self.updateSize()

    def OnCutHere(self, e):
        saveInfo(self.configFile)
        self.error = False
        xSize = self.readVal(self.widthBox)
        bitDiameter = self.readVal(self.trimBitDia)
        bitRadius = bitDiameter / 2.0
        xClear = self.readVal(self.xClear)
        feed = self.readVal(self.feed)
        if not self.error:
            f = self.start("cut0Here", feed, bitDiameter)
            f.write("g0 x%5.3f\n" % (-(bitRadius + xClear)))
            f.write("m0	(pause)\n")
            f.write("g1 z-0.075\n")
            f.write("g1 x%5.3f\n" % (xSize + bitRadius + xClear))
            self.finish(f, -(bitRadius + xClear))
        
    def removeFile(self, fileName):
        fName = os.path.join(self.dirname, fileName + ".ngc")
        print(fName)
        try:
            os.remove(fName)
        except:
            pass
        
    def start(self, fileName, feed, bitDiameter, str=None):
        f = open(os.path.join(self.dirname, fileName + ".ngc"), "w")
        f.write("(%s %s)\n" % 
                (fileName, strftime("%Y-%m-%d %H:%M:%S",localtime())))
        if str != None:
            f.write(str)
        f.write("g55	(coordinate system 2)\n")
        f.write("g20	(units inches)\n")
        f.write("g61	(exact path)\n")
        f.write("g0 z1.0\n")
        f.write("m0	(pause bit %5.3f)\n" % (bitDiameter))
        f.write("s25000	(set spindle speed)\n")
        f.write("m3	(start spindle)\n")
        f.write("g4 p2.0	(wait for spindle to start)\n")
        f.write("f%d	(set feed rate)\n" % (feed))
        return(f)

    def OnCut(self, e):
        saveInfo('config.txt')
        self.error = False
        xSize = self.readVal(self.widthBox)
        ySize = self.readVal(self.yBox)
        yExtra = self.readVal(self.yExtraBox)
        bitDiameter = self.readVal(self.cutBitDia)
        overHang = self.readVal(self.overHang)
        xClear = self.readVal(self.xClear)
        feed = self.readVal(self.feed)
        if not self.error:
            bitRadius = bitDiameter / 2.0
            ruler = ySize + yExtra - overHang
            sixteenths = int(ruler / .0625)
            ruler = sixteenths * .0625
            inches = int(sixteenths / 16)
            sixteenths -= inches * 16
            fract = 16
            if sixteenths != 0:
                while (sixteenths & 1) == 0:
                    sixteenths >>= 1
                    fract >>= 1
                rulerVal = "%d %d/%d" % (inches,sixteenths,fract)
            else:
                rulerVal = "%d" % (inches)
            self.rulerBox.SetValue("%5.3f" % (ruler))
            self.rulerTxt.SetLabel(rulerVal)
            cut = ySize + yExtra - ruler
            bitLoc = cut + bitRadius
            self.status.SetLabel("cut %5.3f bitLoc %5.3f size %5.3f" %
                                 (cut, bitLoc, cut + ruler))
            if bitDiameter < .050:
                xPos = bitDiameter
                f = self.start("cut1", 14, bitDiameter)
                f.write("g0 x%5.3f y%5.3f\n" % (xPos, -bitLoc))
                f.write("m0	(pause)\n")
                f.write("g1 z0.020\n")
                xEnd = xSize - bitDiameter
                xInc = 1.25 * bitDiameter
                count = 0;
                while xPos < xEnd:
                    f.write("g1 z-0.095	(%3d)\n" % (count))
                    f.write("g1 z0.020\n")
                    xPos += xInc
                    count += 1
                    f.write("g1 x%5.3f\n" % (xPos))
            else:
                self.yLocBox.SetValue("%5.3f" % (bitLoc))
                self.yMeasureBox.SetValue("%5.3f" % (ySize + yExtra))
                str = "(size %5.3f ruler %5.3f  %s width %5.3f)\n" % \
                      (ySize, ruler, rulerVal, xSize)
                self.removeFile("cut2Rough")
                self.removeFile("cut3Final")
                f = self.start("cut1", feed, bitDiameter, str)
                if not self.climb.GetValue():
                    f.write("g0 x%5.3f y%5.3f\n" % 
                            (-(bitRadius + xClear), -bitLoc))
                    f.write("g1 z 0.025\n")
                    f.write("m0	(pause ySize %5.3f ruler %5.3f %s)\n" %\
                            (ySize, ruler, rulerVal))
                    f.write("g1 z-0.095\n")
                    f.write("g1 x%5.3f\n" % (xSize + bitRadius + xClear))
                else:
                    f.write("g0 x%5.3f y%5.3f\n" % 
                            ((xSize + bitRadius + xClear), -bitLoc))
                    f.write("g1 z 0.025\n")
                    f.write("m0	(pause ySize %5.3f ruler %5.3f %s)\n" %\
                            (ySize, ruler, rulerVal))
                    f.write("g1 z-0.095\n")
                    f.write("g1 x%5.3f\n" % -(bitRadius + xClear))
            self.finish(f, -(bitRadius + xClear))
        self.sizerV.Layout()

    def OnTrimRough(self, e):
        saveInfo('config.txt')
        self.error = False
        xSize = self.readVal(self.widthBox)
        ySize = self.readVal(self.yBox)
        ruler = self.readVal(self.rulerBox)
        yMeasure = self.readVal(self.yRMeasureBox)
        bitDiameter = self.readVal(self.trimBitDia)
        xClear = self.readVal(self.xClear)
        feed = self.readVal(self.feed)
        if not self.error:
            bitRadius = bitDiameter / 2.0
            # print("ySize %5.3f" % (ySize))
            # print("ruler %5.3f" % (ruler))
            # print("yMeasure %5.3f" % (yMeasure))
            cut = (yMeasure - ruler) - (yMeasure - ySize) / 2.0
            bitLoc = cut + bitRadius
            self.yLocBox.SetValue("%5.3f" % (bitLoc))
            self.status.SetLabel("cut %5.3f bitLoc %5.3f size %5.3f" %
                                 (cut, bitLoc, cut + ruler))
            f = self.start("cut2Rough", feed, bitDiameter)
            f.write("g0 x%5.3f y%5.3f\n" % (-(bitRadius + xClear), -bitLoc))
            f.write("m0	(pause)\n")
            f.write("g1 z-0.075\n")
            f.write("g1 x%5.3f\n" % (xSize + bitRadius + xClear))
            self.finish(f, -(bitRadius + xClear))
        self.sizerV.Layout()


    def OnTrimFinal(self, e):
        saveInfo('config.txt')
        self.error = False
        xSize = self.readVal(self.widthBox)
        ySize = self.readVal(self.yBox)
        # ruler = self.readVal(self.rulerBox)
        yLoc = self.readVal(self.yLocBox)
        yMeasure = self.readVal(self.yMeasureBox)
        bitDiameter = self.readVal(self.trimBitDia)
        xClear = self.readVal(self.xClear)
        feed = self.readVal(self.feed)
        if not self.error:
            bitRadius = bitDiameter / 2.0
            print("ySize %5.3f" % (ySize))
            print("yMeasure %5.3f" % (yMeasure))
            print("yMeasure - ySize %5.3f" % (yMeasure - ySize))
            bitLoc = yLoc - (yMeasure - ySize)
            cut = bitLoc - bitRadius
            ruler = yMeasure - (yLoc - bitRadius)
            self.status.SetLabel("cut %5.3f bitLoc %5.3f ruler %5.3f "\
                                 "size %5.3f" %
                                 (cut, bitLoc, ruler, cut + ruler))
            self.removeFile("cut1")
            self.removeFile("cut2Rough")
            f = self.start("cut3Final", feed, bitDiameter)
            if not self.climb.GetValue():
                f.write("g0 x%5.3f y%5.3f\n" % (-(bitRadius + xClear), \
                                                -bitLoc))
                f.write("g1 z 0.025\n")
                f.write("m0	(pause)\n")
                f.write("g1 z-0.095\n")
                f.write("g1 x%5.3f\n" % (xSize + bitRadius + xClear))
            else:
                f.write("g0 x%5.3f y%5.3f\n" % \
                        (xSize + bitRadius + xClear, -bitLoc))
                f.write("g1 z 0.025\n")
                f.write("m0	(pause)\n")
                f.write("g1 z-0.095\n")
                f.write("g1 x%5.3f\n" % (-(bitRadius + xClear)))
            self.finish(f, -(bitRadius + xClear))
        self.sizerV.Layout()

    def finish(self, f, x):
        f.write("m5	(stop spindle)\n");
        f.write("g0 z1.5\n")
        f.write("g0 x%5.3f y3.5\n" % (x))
        f.write("g54	(coordinate system 1)\n")
        f.write("m2	(end of program)\n");
        f.close()

app = wx.App()

frame = MainFrame(None, 'Cut Board')
frame.Show()

app.MainLoop()
