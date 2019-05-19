from os import path
import numpy as np
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import matplotlib
import matplotlib.ticker as ticker
matplotlib.use("TkAgg")
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pylab import * #imports matplotlib (and ???)
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)


minor_locator = AutoMinorLocator(2)
matplotlib.rcParams.update({'figure.autolayout': True})
dataColor = 'k'  # black
fitColor = 'tab:blue'
diffColor = 'tab:orange'
matplotlib.rc('font', **{'family': "arial"})
graphCounter = 0


def popupmsg(msg, poptitle):
    popup = tk.Tk()
    popup.wm_title(poptitle)
    label = ttk.Label(popup, text=msg, justify='center')
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.resizable(width=False, height=False)

    popup.mainloop()





# python 3 app
class IoPlot(tk.Tk):   # IoPlot will inherit attributes from the tkinter module. the (tk.TK) is not technically necesary

    def __init__(self, *args, **kwargs):  # this is here to always load the following. always run when IoPlot is called
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self,default='PyXRDPlotter.ico')
        tk.Tk.wm_title(self, "PyXRD Plotter")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=0)
        container.grid_columnconfigure(0, weight=0)

        self.frames = {}

        for F in (StartPage, GraphTemplateFrame, MultipleGraphPage):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New session")
        filemenu.add_command(label="Open session")
        filemenu.add_command(label="Save session")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)

        pxrdplotmenu = Menu(menubar, tearoff=0)
        pxrdplotmenu.add_command(label="single graph", command= lambda: self.show_frame(StartPage))
        pxrdplotmenu.add_command(label="multiple graphs", command= lambda: self.show_frame(MultipleGraphPage))
        menubar.add_cascade(label="Plotter options", menu=pxrdplotmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmsg = str("Please see github repo for help: https://github.com/iWHOswald/PyXRD-Plotter")
        aboutmsg = str("PyXRD Plotter version 0.5." '\n' "Coded in Python 3 by Iain W. H. Oswald." '\n' "Github: https://github.com/iWHOswald/PyXRD-Plotter")
        #img = PhotoImage(file="ball.ppm")
        #canvas.create_image(20, 20, anchor=NW, image=img)

        abouttitle = str("About PyXRD Plotter")
        helptitle = str("Help")
        helpmenu.add_command(label="Help", command=lambda: popupmsg(helpmsg, helptitle))
        helpmenu.add_command(label="About...", command= lambda: popupmsg(aboutmsg, abouttitle))
        menubar.add_cascade(label="Help", menu=helpmenu)

        tk.Tk.config(self, menu=menubar)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class Graph:
    hkl_loaded = 0

    def __init__(self):
        pass

    def hklOpen(self):

        if self.NoFileChecker == 0:
            popupmsg("Please import a TOPAS dataset first.", "Error")
            pass
        else:
            self.hkl_file = filedialog.askopenfilename(initialdir="/", title="Select hkl file",
                                                   filetypes=(("hkl files", "*.txt"), ("all files", "*.*")))
            self.arr_hkl = np.genfromtxt(self.hkl_file, dtype='float', delimiter=',', skip_header=1)
            self.ChangeLayout.configure(state=NORMAL)
            self.ticksButton.configure(state=NORMAL)
            self.ticksButton.configure(state=NORMAL)
            self.ticksButton.state(['!alternate'])
            self.ticksButton.state(['selected'])
            self.firstGraphPlot = 0
            Graph.hkl_loaded = 1
            StartPage.LoadGraph(self)
            #return Graph.hkl_loaded

    def fileOpen(self):
        self.TopasFile = filedialog.askopenfilename(initialdir="/", title="Select TOPAS file",
                                               filetypes=(("TOPAS files", "*.txt"), ("all files", "*.*")))

        self.rowSkip = 1
        self.firstGraphPlot = 0

        with open(self.TopasFile, "r") as f: #figure out how much metadata there is
            self.content = f.readlines(300) #300 should definitely cover enough characters to find all meta
            comma_count = str(self.content[1:2]).count(',')
            row_text = str(self.content[:self.rowSkip])
            strip_row_number = str(row_text[:-4])
            print(row_text)
            print(strip_row_number)

            while re.search('[a-zA-Z]', strip_row_number): #counts num of metadata lines; returns rowskip (lines to pass
                self.rowSkip += 1
                row_text = str(self.content[self.rowSkip-1:self.rowSkip])
                strip_row_number = row_text[:-4]
                # print(strip_row_number)

            arr = np.genfromtxt(self.TopasFile, dtype='str', delimiter=',', skip_header=self.rowSkip-2, max_rows=1)
            self.column_count = np.size(arr)
            counter = 4

            for columns in range(self.column_count):
                counter -= 1

            if np.where(arr == "'x"):  # this code determines which columns were exported from topas
                self.x_col = True
                self.x_col_loc = re.findall('[0-9]', str(np.where(arr == "'x")))[0]  # which column x is in
            else:
                self.x_col = False

            if np.where(arr == "Diff"):
                self.diff_col = True
                self.diff_col_loc = re.findall('[0-9]', str(np.where(arr == "Diff")))[0]  # which column diff is in
            else:
                self.diff_col = False

            if np.where(arr == "Ycalc"):
                self.ycalc_col = True
                self.ycalc_col_loc = re.findall('[0-9]', str(np.where(arr == "Ycalc")))[0]  # which column calculated is
            else:
                self.ycalc_col = False

            if arr[1:2] != "'x" and arr[1:2] != "Diff" and arr[1:2] != "Ycalc" and arr[1:2] != "Bkg":  # raw data column
                self.raw_col = True
                self.raw_col_loc = 1
            else:
                self.raw_col = False

            if np.where(arr == "Bkg"):
                self.bkg_col = True
                self.Bkg_col_loc = re.findall('[0-9]', str(np.where(arr == "Bkg")))[0] #which column diff curve is in
            else:
                self.bkg_col = False

            if np.where(arr == "xy_cumchi2"):
                self.cumchi2_col = True
                self.xy_cumchi2_col_loc = re.findall('[0-9]', str(np.where(arr == "xy_cumchi2")))[0] #column xy_cumchi2 is in
            else:
                self.cumchi2_col = False

        self.NoFileChecker = 1

        self.hkl_button.configure(state=NORMAL)
        self.UpdateGraph.configure(state=NORMAL)
        self.SaveFig.configure(state=NORMAL)
        self.LegendLocater.config(state=NORMAL)
        self.LegendTextSize.configure(state=NORMAL)
        self.AxesTextSize.configure(state=NORMAL)
        self.AxeslblTextSize.configure(state=NORMAL)
        self.xAxeslbl.configure(state=NORMAL)
        self.yAxeslbl.configure(state=NORMAL)

        StartPage.dialogueBox(self)
        StartPage.LoadGraph(self)


class StartPage(Graph, tk.Frame):

    def __init__(self, parent, controller): # setup the layout of the page
        tk.Frame.__init__(self, parent)
        print("single graph page")
        self.graphCounter = 0
        self.LegendBool = 0
        self.legLoc = "upper right"
        self.allSized = 18 #default size of all text
        self.LegendTextSizeValue = 18  # Whatever you want all the text size to be.
        gridcounter = 0  # This is what allows you to easily add new grid elements; just add gridcounter +=1
        self.GraphCount = 1  # default value of amount of graphs to be plotted
        self.NoFileChecker = 0 # looks to see at least 1 Topas file has been loaded at all; 0 = none loaded

        # this stuff takes care of setting up the data set entry drop down menu. Location etc #


        upload_button = ttk.Button(self, text="Open TOPAS file",command=lambda: self.fileOpen())
        upload_button.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        gridcounter += 1

        self.hkl_button = ttk.Button(self, text="Open hkl file", command=lambda: self.hklOpen())
        self.hkl_button.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        if self.NoFileChecker == 0:
            self.hkl_button.configure(state=DISABLED)
        gridcounter += 1

        self.ChangeLayout = ttk.Button(self, text="setup hkl layout",
                        command=lambda: controller.show_frame(GraphTemplateFrame))
        self.ChangeLayout.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        if self.hkl_loaded == 0:
            self.ChangeLayout.configure(state=DISABLED)
        gridcounter += 1

        graphPropertieslbl = Label(self, text="Graph properties:")
        graphPropertieslbl.grid(sticky=W, row=gridcounter, column=0)
        gridcounter += 1

        xRange = Label(self, text="x-axis range (2theta):")
        xRange.grid(sticky=W, row=gridcounter, column=0)
        self.xRangeLow = Entry(self, width=3)
        self.xRangeLow.grid(sticky=W, row=gridcounter, column=1)
        self.xRangeLow.config(state=DISABLED) # set initial state to disabled before graph is loaded
        xRangeTo = Label(self, text="to")
        xRangeTo.grid(sticky=W, row=gridcounter, column=2)
        self.xRangeHigh = Entry(self, width=3)
        self.xRangeHigh.grid(sticky=W, row=gridcounter, column=3)
        self.xRangeHigh.config(state=DISABLED) # set initial state to disabled before graph is loaded
        gridcounter += 1

        yRange = Label(self, text="y-axis range (intensity):")
        yRange.grid(sticky=W, row=gridcounter, column=0)
        self.yRangeLow = Entry(self, width=5)
        self.yRangeLow.grid(sticky=W, row=gridcounter, column=1)
        self.yRangeLow.config(state=DISABLED) # set initial state to disabled before graph is loaded
        yRange = Label(self, text="to", anchor=W, justify=LEFT)
        yRange.grid(sticky=W, row=gridcounter, column=2)
        self.yRangeHigh = Entry(self, width=5)
        self.yRangeHigh.grid(sticky=W, row=gridcounter, column=3)
        self.yRangeHigh.config(state=DISABLED) # set initial state to disabled before graph is loaded
        gridcounter += 1

        xTickTogglelbl = Label(self, text="Specify x-axis ticks:")
        xTickTogglelbl.grid(sticky=W, row=gridcounter, column=0)
        self.xTickToggle = ttk.Checkbutton(self, command=lambda: self.SetxTickState())
        self.xTickToggle.state(['!alternate'])
        self.xTickToggle.state(['!selected'])
        self.xTickToggle.config(state=DISABLED) # set initial state to disabled before graph is loaded
        self.xTickToggle.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        yTickTogglelbl = Label(self, text="Specify y-axis ticks:")
        yTickTogglelbl.grid(sticky=W, row=gridcounter, column=0)
        self.yTickToggle = ttk.Checkbutton(self, command=lambda: self.SetyTickState())
        self.yTickToggle.state(['!alternate'])
        self.yTickToggle.state(['!selected'])
        self.yTickToggle.config(state=DISABLED) # set initial state to disabled before graph is loaded
        self.yTickToggle.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        xMjTicklbl = Label(self, text="x- major/minor tick interval:")
        xMjTicklbl.grid(sticky=W, row=gridcounter, column=0)
        self.xMjTick = Entry(self, width=3)
        self.xMjTick.grid(sticky=W, row=gridcounter, column=1)
        self.xMjTick.insert(0, "0") # set initial state to disabled before graph is loaded
        self.xMjTick.config(state=DISABLED)
        xMjTicklbl2 = Label(self, text="/", anchor=W, justify=LEFT)
        xMjTicklbl2.grid(sticky=W, row=gridcounter, column=2)
        self.xMiTick = Entry(self, width=3)
        self.xMiTick.grid(sticky=W, row=gridcounter, column=3)
        self.xMiTick.insert(0, "0") # set initial state to disabled before graph is loaded
        self.xMiTick.config(state=DISABLED)
        gridcounter += 1

        yMjTicklbl = Label(self, text="y- major/minor tick interval:")
        yMjTicklbl.grid(sticky=W, row=gridcounter, column=0)
        self.yMjTick = Entry(self, width=5)
        self.yMjTick.grid(sticky=W, row=gridcounter, column=1)
        self.yMjTick.insert(0, "0") # set initial state to disabled before graph is loaded
        self.yMjTick.config(state=DISABLED)
        yMjTicklbl2 = Label(self, text="/", anchor=W, justify=LEFT)
        yMjTicklbl2.grid(sticky=W, row=gridcounter, column=2)
        self.yMiTick = Entry(self, width=5)
        self.yMiTick.grid(sticky=W, row=gridcounter, column=3)
        self.yMiTick.insert(0, "0") # set initial state to disabled before graph is loaded
        self.yMiTick.config(state=DISABLED)
        gridcounter += 1

        ticksButtonlbl = Label(self, text="Show hkl ticks:")
        ticksButtonlbl.grid(sticky=W, row=gridcounter, column=0)
        self.ticksButton = ttk.Checkbutton(self, command=lambda: StartPage.hklToggle(self))
        self.ticksButton.grid(sticky=W, row=gridcounter, column=1)
        if Graph.hkl_loaded == 1:
            self.ticksButton.state(['!alternate'])
            self.ticksButton.state(['selected'])
        else:
            self.ticksButton.configure(state=DISABLED)
        gridcounter += 1

        ticksoffsetlbl = Label(self, text="hkl ticks offset:")
        ticksoffsetlbl.grid(sticky=W, row=gridcounter, column=0)
        self.ticksButtonOffset = ttk.Entry(self, width=5)
        self.ticksButtonOffset.insert(0, "0")
        self.ticksButtonOffset.grid(sticky=W, row=gridcounter, column=1)
        if Graph.hkl_loaded == 1:
            self.ticksButtonOffset.state(['!alternate'])
            self.ticksButtonOffset.state(['selected'])
        else:
            self.ticksButtonOffset.configure(state=DISABLED)
        gridcounter += 1

        hklticklengthlbl = Label(self, text="hkl ticks size:")
        hklticklengthlbl.grid(sticky=W, row=gridcounter, column=0)
        self.hklticklength = ttk.Entry(self, width=5)
        self.hklticklength.insert(0, "0")
        self.hklticklength.grid(sticky=W, row=gridcounter, column=1)
        if Graph.hkl_loaded == 1:
            self.hklticklength.state(['!alternate'])
            self.hklticklength.state(['selected'])
        else:
            self.hklticklength.configure(state=DISABLED)
        gridcounter += 1

        DiffCurveButtonlbl = Label(self, text="Show difference curve:")
        DiffCurveButtonlbl.grid(sticky=W, row=gridcounter, column=0)
        self.DiffCurveButton = ttk.Checkbutton(self, command=lambda: StartPage.SetDiffCurvState(self))
        self.DiffCurveButton.state(['!alternate'])
        self.DiffCurveButton.state(['selected'])
        self.DiffCurveButton.config(state=DISABLED) # set initial state to disabled before graph is loaded
        self.DiffCurveButton.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        DiffCurveOffsetlbl = Label(self, text="Difference Curve offset:")
        DiffCurveOffsetlbl.grid(sticky=W, row=gridcounter, column=0)
        self.DiffCurveOffset = ttk.Entry(self, width=5)
        self.DiffCurveOffset.insert(0, "0")
        self.DiffCurveOffset.config(state=DISABLED) # set initial state to disabled before graph is loaded
        self.DiffCurveOffset.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        CompressDiffLbl = Label(self, text="Compress Diff curve:")
        CompressDiffLbl.grid(sticky=W, row=gridcounter, column=0)
        self.CompressDiffEntry = ttk.Entry(self, width=5)
        self.CompressDiffEntry.insert(1, "1")
        self.CompressDiffEntry.config(state=DISABLED) # set initial state to disabled before graph is loaded
        self.CompressDiffEntry.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

    # this stuff takes care of setting up the legend. Location etc #
        self.LegendLocater = ttk.Menubutton(self, text="Legend Position")
        self.LegendLocater.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        self.LegendLocater.config(state=DISABLED)
        self.LegendLocater.menu = Menu(self.LegendLocater, tearoff=0)
        self.LegendLocater["menu"] = self.LegendLocater.menu
        self.LegendTopRight = tk.IntVar()
        self.LegendTopLeft = tk.IntVar()
        self.LegendBotLeft = tk.IntVar()
        self.LegendBotRight = tk.IntVar()
        self.LegendOff = tk.IntVar()

        self.LegendLocater.menu.add_checkbutton(label="Top right", variable=self.LegendTopRight, command=lambda: StartPage.LegendTR(self))
        self.LegendLocater.menu.add_checkbutton(label="Top left", variable=self.LegendTopLeft, command=lambda: StartPage.LegendTL(self))
        self.LegendLocater.menu.add_checkbutton(label="Bottom right",variable=self.LegendBotRight, command=lambda: StartPage.LegendBR(self))
        self.LegendLocater.menu.add_checkbutton(label="Bottom left", variable=self.LegendBotLeft, command=lambda: StartPage.LegendBL(self))
        self.LegendLocater.menu.add_checkbutton(label="Turn legend off", variable=self.LegendOff, command=lambda: StartPage.LegendLO(self))
        gridcounter += 1

        LegendTextSizelbl = Label(self, text="Legend text size:")
        LegendTextSizelbl.grid(sticky=W, row=gridcounter, column=0)
        self.LegendTextSize = Entry(self, width=3)
        self.LegendTextSize.insert(18, "18")
        self.LegendTextSize.configure(state=DISABLED)
        self.LegendTextSize.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        AxesTextSizelbl = Label(self, text="Axes text size:")
        AxesTextSizelbl.grid(sticky=W, row=gridcounter, column=0)
        self.AxesTextSize = Entry(self, width=3)
        self.AxesTextSize.insert(18, "18")
        self.AxesTextSize.configure(state=DISABLED)
        self.AxesTextSize.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        AxeslblTextSizelbl = Label(self, text="Axis label text size:")
        AxeslblTextSizelbl.grid(sticky=W, row=gridcounter, column=0)
        self.AxeslblTextSize = Entry(self, width=3)
        self.AxeslblTextSize.insert(18, "18")
        self.AxeslblTextSize.configure(state=DISABLED)
        self.AxeslblTextSize.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        self.xAxeslbl = ttk.Button(self, text="modify x-axis label", command=lambda: StartPage.popaxismsg(self, "Edit x-axis label:", "Edit x-axis label"))
        self.xAxeslbl.grid(sticky=NW, row=gridcounter, column=0, pady=2, padx=2)
        self.xAxeslbl.configure(state=DISABLED)
        gridcounter += 1

        self.yAxeslbl = ttk.Button(self, text="modify y-axis label", command=lambda: StartPage.popaxismsg(self))
        self.yAxeslbl.grid(sticky=NW, row=gridcounter, column=0, pady=2, padx=2)
        self.yAxeslbl.configure(state=DISABLED)
        gridcounter += 1

        self.UpdateGraph = ttk.Button(self, text="Update graph", command=lambda: StartPage.LoadGraph(self))
        self.UpdateGraph.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        if self.NoFileChecker == 0:
            self.UpdateGraph.configure(state=DISABLED)
        else:
            self.UpdateGraph.configure(state=NORMAL)
        gridcounter += 1

        self.SaveFig = ttk.Button(self, text="Save figure", command=lambda: StartPage.saveFigFunc(self))
        self.SaveFig.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        if self.NoFileChecker == 0:
            self.SaveFig.configure(state=DISABLED)
        gridcounter += 1

        dialoguelbl = Label(self, text="Datasets currently open:")
        dialoguelbl.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        gridcounter += 1

        self.gridcounter2 = gridcounter
        dialoguelbl = Label(self, text=StartPage.dialogueBox(self))
        dialoguelbl.grid(sticky=NW, row=self.gridcounter2, column=0, pady=4, padx=4, columnspan=2)
        gridcounter += 1

    def popaxismsg(self, msg, poptitle):
        gridcounter = 0
        popup = tk.Tk()
        popup.wm_title(poptitle)
        label = ttk.Label(popup, text=msg, justify='left')
        label.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4, columnspan=2)
        gridcounter += 1
        # this stuff takes care of setting up the common labels. Location etc #
        commonlabelmenu = ttk.Menubutton(popup, text="Common labels")
        commonlabelmenu.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        commonlabelmenu.config(state=NORMAL)
        commonlabelmenu.menu = Menu(commonlabelmenu, tearoff=0)
        commonlabelmenu["menu"] = commonlabelmenu.menu
        commonlabelmenuCu = tk.IntVar()
        commonlabelmenuQ = tk.IntVar()
        commonlabelmenud = tk.IntVar()
        commonlabelmenuth = tk.IntVar()
        Cu = 1
        Q = 2
        d = 3
        th = 4

        commonlabelmenu.menu.add_checkbutton(label="2θ (°, CuKα)", variable=commonlabelmenuCu,
                                             command=lambda: StartPage.commonlabelfunc(self, Cu))
        commonlabelmenu.menu.add_checkbutton(label="Q (Å-1)", variable=commonlabelmenuQ,
                                             command=lambda: StartPage.commonlabelfunc(self, Q))
        commonlabelmenu.menu.add_checkbutton(label="d (Å)", variable=commonlabelmenud,
                                             command=lambda: StartPage.commonlabelfunc(self, d))
        commonlabelmenu.menu.add_checkbutton(label="2θ (°)", variable=commonlabelmenuth,
                                             command=lambda: StartPage.commonlabelfunc(self, th))
        gridcounter += 1
        B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
        B1.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4, columnspan=2)
        popup.resizable(width=500, height=400)

        popup.mainloop()

    def commonlabelfunc(self, label):
        if label == 1:
            self.xlabel = str('dsgdsgds2$\Theta$ ($^\circ$, CuK$_{\\alpha}$)')
            return self.xlabel
        if label == 2:
            self.xlabel = str('Q (r’$\AA$’$10-1$')
            return self.xlabel

        if label == 3:
            self.xlabel = str('d (r’$\AA$’')
            return self.xlabel

        if label == 4:
            self.xlabel = str('2$\Theta$ ($^\circ$)')
            return self.xlabel


    def dialogueBox(self):
        if self.NoFileChecker == 0:
            self.datasetString = str("No datasets loaded.")
            return self.datasetString
        else:
            self.datasetString = str(path.basename(self.TopasFile))
            dialoguelbl = Label(self, text=self.datasetString)
            dialoguelbl.grid(sticky=NW, row=self.gridcounter2, column=0, pady=4, padx=4, columnspan=2)
            return self.datasetString

    def CheckGraphCounter(self):
        print(self.GraphCount)
        self.GraphCount = self.GraphCount

    def LegendTR(self):
        self.LegendTopLeft.set(0)
        self.LegendBotLeft.set(0)
        self.LegendBotRight.set(0)
        self.LegendOff.set(0)
        self.legLoc = 'upper right'  # location of the legend
        self.LegendBool = 0

    def LegendTL(self):
        self.LegendTopRight.set(0)
        self.LegendBotLeft.set(0)
        self.LegendBotRight.set(0)
        self.LegendOff.set(0)
        self.legLoc = 'upper left'  # location of the legend
        self.LegendBool = 0

    def LegendBR(self):
        self.LegendTopLeft.set(0)
        self.LegendTopRight.set(0)
        self.LegendBotLeft.set(0)
        self.LegendOff.set(0)
        self.legLoc = 'lower right'  # location of the legend
        self.LegendBool = 0

    def LegendBL(self):
        self.LegendTopLeft.set(0)
        self.LegendTopRight.set(0)
        self.LegendBotRight.set(0)
        self.LegendOff.set(0)
        self.legLoc = 'lower left'  # location of the legend
        self.LegendBool = 0

    def LegendLO(self):
        self.LegendTopLeft.set(0)
        self.LegendTopRight.set(0)
        self.LegendBotLeft.set(0)
        self.LegendBotRight.set(0)
        self.LegendBool = 1

    def LoadGraph(self):
        self.ylabel = 'Intensity (Counts)'
        self.xlabel = '2$\Theta$ ($^\circ$, CuK$_{\\alpha}$)'

        #setup the graphical elements; fonts, colors, etc
        matplotlib.rc('font', size=self.allSized, **{'family': "arial"})  # controls default text sizes
        matplotlib.rc('legend', fontsize=self.allSized)  # legend fontsize
        matplotlib.rc('xtick', labelsize=self.allSized)  # fontsize of the tick labels
        matplotlib.rc('ytick', labelsize=self.allSized)  # fontsize of the tick labels
        matplotlib.rc('axes', titlesize=self.allSized)  # fontsize of the axes title
        matplotlib.rc('axes', labelsize=self.allSized)  # fontsize of the x and y labels
        matplotlib.rc('figure', titlesize=self.allSized)  # fontsize of the figure title


        self.diffColor = "blue"
        self.fitColor = "red"
        self.dataColor = "black"
        self.arr_graph = np.loadtxt(self.TopasFile, delimiter=',', dtype='float', skiprows=self.rowSkip - 1,
                                    unpack=True)
        self.f = Figure(figsize=(6, 6), dpi=100)
        self.ax1 = self.f.add_subplot(111)

        #self.ax1.ticklabel_format(axis='y', style='sci', scilimits=(-10,10), useOffset=True, useLocale=None,
        #                      useMathText=True)

        self.x_axis_min = np.min(
            self.arr_graph[int(self.x_col_loc)])  # find min value of x-axis; to scale initial graph
        self.x_axis_max = np.max(
            self.arr_graph[int(self.x_col_loc)])  # find max value of x-axis; to scale initial graph
        self.y_calc_min = np.min(
            self.arr_graph[int(self.ycalc_col_loc)])  # find min value of calc curve; to scale initial graph
        self.y_calc_max = np.max(
            self.arr_graph[int(self.ycalc_col_loc)])  # find max value of calc curve; to scale initial graph
        self.y_raw_min = np.min(
            self.arr_graph[int(self.raw_col_loc)])  # find min value of raw curve; to scale initial graph
        self.y_raw_max = np.max(
            self.arr_graph[int(self.raw_col_loc)])  # find max value of raw curve; to scale initial graph

        if self.diff_col:
            self.diff_min = np.min(self.arr_graph[int(self.diff_col_loc)]) # find max value of diff curve; to scale initial graph
            self.diff_max = np.max(self.arr_graph[int(self.diff_col_loc)]) # find max value of diff curve; to scale initial graph
            self.diff_total = abs(self.diff_min) + abs(self.diff_max)
            self.compressedDiff = (self.arr_graph[int(self.diff_col_loc)] * float(self.CompressDiffEntry.get()))

        else:
            self.diff_min = 0
            self.diff_max = 0

        if self.y_calc_max >= self.y_raw_max:  # figure out if the calculated or raw has the highest y value to correctly plot
            y_max = int(round(self.y_calc_max))
        else:
            y_max = int(round(self.y_raw_max))

        if self.x_col: #  this plots the lines
            if self.raw_col:
                self.ax1.plot(self.arr_graph[int(self.x_col_loc)], self.arr_graph[1],
                              color=self.dataColor, marker='o', lineStyle='None', label='Data', markersize=2)
            else:
                print("there is no raw data")
            if self.ycalc_col:
                self.ax1.plot(self.arr_graph[int(self.x_col_loc)], self.arr_graph[int(self.ycalc_col_loc)],
                              color=self.fitColor, lineStyle='-', label='Calculated', lineWidth='1.5')
            else:
                print("there is no ycalc data")
            if self.diff_col:
                self.diff_offset = int(self.diff_max)
                a = self.ax1.plot(self.arr_graph[int(self.x_col_loc)], (self.arr_graph[int(self.diff_col_loc)]) - self.diff_max,
                              color=self.diffColor, lineStyle='-', label='Difference', lineWidth='1')
            else:
                print("there is no diff data")
            if self.hkl_loaded == 1:
                b = self.ax1.plot(self.arr_hkl, (self.arr_hkl - self.arr_hkl),
                              color=self.fitColor, marker='|', label='hkl phase', linestyle='None', markerSize=14)
            else:
                print("there is no hkl data")
        else:
            print("there is no x-axis data")


        if self.firstGraphPlot == 0: #run this code to setup the initial graph or loading in hkl ticks

            # setup the axes to be plotted based on graph data; tries to plot data as good as possible

            y_max = y_max * 1.1  # this adds a wee bit of white space between highest data point and axis box
            self.ax1.set_xlim(self.x_axis_min, self.x_axis_max)  # setup the graph to scale x-axes appropriately

            if self.diff_col: #this figures out the y min/max when a diff curve is present
                if self.hkl_loaded == 1: # configure the state of things for the hkl loaded in
                    self.ticksButton.configure(state=NORMAL)
                    self.ticksButton.state(['!alternate'])
                    self.ticksButton.state(['selected'])
                    self.ticksButtonOffset.config(state=NORMAL)  # turn on when graph is loaded
                    self.ticksButtonOffset.delete(0, 'end')
                    self.hklticklength.configure(state=NORMAL)
                    self.hklticklength.delete(0, 'end')

                    for handle in a:
                        handle.remove()
                    for handle in b:
                        handle.remove()

                    for tick in self.arr_hkl:
                        self.hkl_tick_length = round(abs(y_max) * 0.04)
                        self.hkl_tick_min = round((abs(self.y_calc_min) - (self.hkl_tick_length * 1.4)))
                        self.hkl_tick_max = self.hkl_tick_length + self.hkl_tick_min

                        self.ax1.vlines(x=tick, ymin=self.hkl_tick_min, ymax=self.hkl_tick_max, linewidth=1, color='r')

                    a = self.ax1.plot(self.arr_graph[int(self.x_col_loc)],
                                      self.compressedDiff + ((-1*(abs(self.hkl_tick_min) + abs(self.diff_max)))*1.1),
                                      color=self.diffColor, lineStyle='-', label='Difference', lineWidth='1')
                    y_min = (abs(self.diff_min) + ((abs(self.hkl_tick_min) + abs(self.diff_max)))*1.1) * -1.1     # set y-min based on values of diff and hkl ticks

                    self.ticksButtonOffset.insert(0, int((-1*(abs(self.hkl_tick_min))))) #  set the initial values for
                    self.hklticklength.insert(0, int(self.hkl_tick_length))
                    self.DiffCurveOffsetNew = (-1*(abs(self.hkl_tick_min) + abs(self.diff_max)))

                else:
                    self.hkl_tick_min = 0
                    y_min = self.y_calc_min - (self.diff_total * 1.1)

                self.ax1.set_ylim(y_min, y_max)  # setup the graph to scale y axes appropriately

                self.DiffCurveButton.configure(state=NORMAL)
                self.DiffCurveButton.state(['!alternate'])
                self.DiffCurveButton.state(['selected'])
                self.CompressDiffEntry.config(state=NORMAL)  # set initial state to disabled before graph is loaded
                self.DiffCurveOffset.config(state=NORMAL)  # set initial state to enabled now that graph data is loaded
                self.DiffCurveOffset.delete(0, "") #clears any value here before
                self.DiffCurveOffset.insert(0, int(((-1*(abs(self.hkl_tick_min) + abs(self.diff_max)))*1.1))) # set diff curve value in box

            elif self.diff_col == False: #this figures out the y min/max when no diff curve
                y_min = self.y_calc_min * -1.2
                if self.hkl_loaded == 1:
                    y_min = y_min - self.hkl_tick_offset

                self.ax1.set_ylim(y_min, y_max)  # setup the graph to scale y and x-axes appropriately

            elif self.diff_col and self.NoFileChecker > 1:
                pass

            #  The following strictly turns on the entry fields and fills them with the pre-determined values  #

            self.xRangeLow.delete(0, 'end') #clear the entries in case previous ones were existing (like loading in a new graph)
            self.xRangeHigh.delete(0, 'end')
            self.yRangeLow.delete(0, 'end')
            self.yRangeHigh.delete(0, 'end')
            self.xRangeLow.config(state=NORMAL)  # set initial state to enabled now that graph data is loaded
            self.xRangeLow.insert(0, int(round(self.x_axis_min)))  # and stick starting x-min in
            self.xRangeHigh.config(state=NORMAL)  # set initial state to enabled now that graph data is loaded
            self.xRangeHigh.insert(0, int(round(self.x_axis_max)))  # enable and stick starting x-max in

            self.yRangeLow.config(state=NORMAL)  # set initial state to disabled before graph is loaded
            self.yRangeLow.delete(0, 'end')  # clears any value here before
            self.yRangeLow.insert(1, int(y_min))  # enable and stick starting x-max in
            self.yRangeHigh.config(state=NORMAL)  # set initial state to disabled before graph is loaded
            self.yRangeHigh.delete(0, 'end')  # clears any value here before
            self.yRangeHigh.insert(1, int(y_max))  # enable and stick starting x-max in

            self.ax1.xaxis.set_major_locator(ticker.AutoLocator())  # when first plotted, will use autolocator.
            self.ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator())  # when first plotted, will use autolocator.

            #turn on the rest of the options for the graph
            self.xTickToggle.config(state=NORMAL)  # turn on when graph is loaded
            self.xTickToggle.state(['!alternate'])
            self.xTickToggle.state(['selected'])

            self.yTickToggle.config(state=NORMAL)  # turn on when graph is loaded
            self.yTickToggle.state(['!alternate'])
            self.yTickToggle.state(['selected'])

            self.xMjTick.config(state=NORMAL) #  turn on tick stuff
            self.xMiTick.config(state=NORMAL)
            self.yMjTick.config(state=NORMAL)
            self.yMiTick.config(state=NORMAL)
            self.xMjTick.delete(0, 'end')
            self.xMiTick.delete(0, 'end')
            self.yMjTick.delete(0, 'end')
            self.yMiTick.delete(0, 'end')

            if y_max <= 100:
                yMjTickCalc = 10
            elif y_max > 100 and y_max <= 1000:
                yMjTickCalc = 100
            elif y_max > 1000 and y_max <= 10000:
                yMjTickCalc = 1000
            elif y_max > 10000 and y_max <= 100000:
                yMjTickCalc = 10000
            xMjTickCalc = int(round(self.x_axis_max / 10))
            xMiTickCalc = float(xMjTickCalc / 2)
            #yMjTickCalc = int(10 * round(y_max/ 10))
            yMiTickCalc = int(yMjTickCalc / 2)

            self.xMjTick.insert(1, str(xMjTickCalc))
            self.xMiTick.insert(1, str(xMiTickCalc))
            self.yMjTick.insert(1, str(yMjTickCalc))
            self.yMiTick.insert(1, str(yMiTickCalc))

            self.firstGraphPlot = 1

        else: #run this code to update graph
           # self.f = Figure(figsize=(6, 6), dpi=100)
           # self.f.autolayout: True
           # self.ax1 = self.f.add_subplot(111)
            self.xRangeLowValue = int(self.xRangeLow.get())
            self.xRangeHighValue = int(self.xRangeHigh.get())
            self.yRangeLowValue = int(self.yRangeLow.get())
            self.yRangeHighValue = int(self.yRangeHigh.get())
            self.DiffCurveOffsetValue = int(self.DiffCurveOffset.get())

            if self.diff_col:
                for handle in a: #removes the current diff curve as this function moves it based on the following
                    handle.remove()

                if self.DiffCurveButton.instate(['selected']) == TRUE: # checks if show diff is true
                    a = self.ax1.plot(self.arr_graph[int(self.x_col_loc)], # plots curve based on offset value
                                           (self.arr_graph[int(self.diff_col_loc)] * float(self.CompressDiffEntry.get())) + self.DiffCurveOffsetValue,
                                           color=self.diffColor, lineStyle='-', label='Difference', linewidth='1')
                else:
                    print("curve has been deleted") # code w/ handle above has already deleted line, so just pass
            if self.hkl_loaded == 1:
                for handle in b: #removes the current diff curve as this function moves it based on the following
                    handle.remove()
                if self.ticksButton.instate(['selected']) == TRUE: # checks if show diff is
                    self.ticksUpdateOffset = float(self.ticksButtonOffset.get())
                    self.hkl_tick_length = round(abs(y_max) * 0.04)
                    #self.hkl_tick_min = round((abs(self.y_calc_min) - (self.hkl_tick_length * 1.4)))
                    self.hkl_tick_max = int(self.hklticklength.get()) + self.ticksUpdateOffset

                    for tick in self.arr_hkl:
                        self.ax1.vlines(x=tick, ymin=self.ticksUpdateOffset, ymax=self.hkl_tick_max, linewidth=1, color='r')

                    print(self.DiffCurveOffsetValue)
                else:
                    print("curve has been deleted") # code w/ handle above has already deleted line, so just pass

            self.ax1.set_xlim(self.xRangeLowValue, self.xRangeHighValue)
            self.ax1.set_ylim(self.yRangeLowValue, self.yRangeHighValue)
            if self.xTickToggle.instate(['selected']) == TRUE:
                self.ax1.xaxis.set_major_locator(ticker.MultipleLocator(float(self.xMjTick.get())))
                self.ax1.xaxis.set_minor_locator(ticker.MultipleLocator(float(self.xMiTick.get())))
            else:
                self.ax1.xaxis.set_major_locator(ticker.AutoLocator())
                self.ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator())

            if self.yTickToggle.instate(['selected']) == TRUE:
                self.ax1.yaxis.set_major_locator(ticker.MultipleLocator(float(self.yMjTick.get())))
                self.ax1.yaxis.set_minor_locator(ticker.MultipleLocator(float(self.yMiTick.get())))
            else:
                self.ax1.yaxis.set_major_locator(ticker.AutoLocator())
                self.ax1.yaxis.set_minor_locator(ticker.AutoMinorLocator())


        if self.LegendBool == 1:
            self.ax1.legend().remove()
        else:
            self.ax1.legend(loc=self.legLoc, prop={'size': self.LegendTextSize.get()}, frameon=False, bbox_transform=plt.gcf().transFigure)

        #  these set the font sizes & labels for axes and axes labels
        #'Intensity (Counts)'
        #'2$\Theta$ ($^\circ$, CuK$_{\\alpha}$)'
        self.ax1.set_ylabel(self.ylabel, size=self.AxeslblTextSize.get())
        self.ax1.set_xlabel(self.xlabel, size=self.AxeslblTextSize.get())
        print(self.xlabel)
        self.ax1.tick_params(axis='both', which='major', labelsize=self.AxesTextSize.get())


        canvas = FigureCanvasTkAgg(self.f, self)
        canvas.draw()
        canvas._tkcanvas.grid(row=0, column=3, columnspan=1000, rowspan=1000, padx=50, pady=5)
        self.firstGraphPlot = 1  # this makes sure you will only update the plot from now on using the following
        print("can you plot")
        self.NoFileChecker = 2

    def hklToggle(self):
        if self.ticksButton.instate(['selected']):
            self.ticksButtonOffset.config(state=NORMAL)
        elif self.ticksButton.instate(['!selected']):
            self.ticksButtonOffset.config(state=DISABLED)

    def SetxTickState(self):
        if self.xTickToggle.instate(['selected']):
            self.xMjTick.config(state=NORMAL)
            self.xMiTick.config(state=NORMAL)

        elif self.xTickToggle.instate(['!selected']):
            self.xMjTick.config(state=DISABLED)
            self.xMiTick.config(state=DISABLED)

    def SetyTickState(self):
        if self.yTickToggle.instate(['selected']):
            self.yMjTick.config(state=NORMAL)
            self.yMiTick.config(state=NORMAL)

        elif self.yTickToggle.instate(['!selected']):
            self.yMjTick.config(state=DISABLED)
            self.yMiTick.config(state=DISABLED)

    def SetDiffCurvState(self):
        if self.DiffCurveButton.instate(['selected']):
            self.DiffCurveOffset.config(state=NORMAL)
            self.CompressDiffEntry.config(state=NORMAL)
        elif self.DiffCurveButton.instate(['!selected']):
            self.DiffCurveOffset.config(state=DISABLED)
            self.CompressDiffEntry.config(state=DISABLED)

    def saveFigFunc(self):
        self.SaveFig = filedialog.asksaveasfilename(initialdir="/", title="save figure name:",
                                                filetypes=(("png", "*.png"), ("all files", "*.*")))
        self.f.savefig(self.SaveFig, dpi=300, facecolor='white', bbox_inches='tight')

    def initiateGraph(self):

        if self.graphCounter == 0:
            # graph_1.LoadGraph()
            graph_1 = Graph()
            graph_1.fileOpen()
            self.graphCounter = 1
        elif graphCounter == 1:
            graph_2 = Graph()
            graph_2()
            self.graphCounter = 2
        elif graphCounter == 2:
            graph_3 = Graph()
            graph_3()
            self.graphCounter = 3
        elif graphCounter == 3:
            graph_4 = Graph()
            graph_4()
            self.graphCounter = 4


class MultipleGraphPage(Graph, tk.Frame):

    def __init__(self, parent, controller): # setup the layout of the page
        tk.Frame.__init__(self, parent)
        self.graphCounter = 0
        self.LegendBool = 0
        self.legLoc = "upper right"
        self.allSized = 18 #default size of all text
        self.LegendTextSizeValue = 18  # Whatever you want all the text size to be.
        gridcounter = 0  # This is what allows you to easily add new grid elements; just add gridcounter +=1
        self.GraphCount = 1  # default value of amount of graphs to be plotted
        self.NoFileChecker = 0 # looks to see at least 1 Topas file has been loaded at all; 0 = none loaded

        # this stuff takes care of setting up the data set entry drop down menu. Location etc #
        numGraphslbl = Label(self, text="Number of datasets:")
        numGraphslbl.grid(sticky=W, row=gridcounter, column=0)
        Graph2mod = Spinbox(self, state="readonly", width=2, from_=2, to=6)
        Graph2mod.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        ChangeLayout = ttk.Button(self, text="setup graph layout",
                        command=lambda: controller.show_frame(GraphTemplateFrame))
        ChangeLayout.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        gridcounter += 1

        upload_button = ttk.Button(self, text="Open TOPAS file",command=lambda: self.fileOpen())
        upload_button.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        gridcounter += 1

        self.hkl_button = ttk.Button(self, text="Open hkl file", command=lambda: self.hklOpen())
        self.hkl_button.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        gridcounter += 1

        graphPropertieslbl = Label(self, text="Graph properties:")
        graphPropertieslbl.grid(sticky=W, row=gridcounter, column=0)

        xRange = Label(self, text="x-axis range (2theta):")
        xRange.grid(sticky=W, row=gridcounter, column=0)
        self.xRangeLow = Entry(self, width=3)
        self.xRangeLow.insert(5, "5")
        self.xRangeLow.grid(sticky=W, row=gridcounter, column=1)
        xRangeTo = Label(self, text="to")
        xRangeTo.grid(sticky=W, row=gridcounter, column=2)
        self.xRangeHigh = Entry(self, width=3)
        self.xRangeHigh.insert(50, "50")
        self.xRangeHigh.grid(sticky=W, row=gridcounter, column=3)
        gridcounter += 1

        yRange = Label(self, text="y-axis range (intensity):")
        yRange.grid(sticky=W, row=gridcounter, column=0)
        self.yRangeLow = Entry(self, width=5)
        self.yRangeLow.grid(sticky=W, row=gridcounter, column=1)
        self.yRangeLow.insert(-2000, "-2000")
        yRange = Label(self, text="to", anchor=W, justify=LEFT)
        yRange.grid(sticky=W, row=gridcounter, column=2)
        self.yRangeHigh = Entry(self, width=5)
        self.yRangeHigh.grid(sticky=W, row=gridcounter, column=3)
        self.yRangeHigh.insert(6000, "6000")
        gridcounter += 1

        xTickTogglelbl = Label(self, text="Specify x-axis ticks:")
        xTickTogglelbl.grid(sticky=W, row=gridcounter, column=0)
        self.xTickToggle = ttk.Checkbutton(self, command=lambda: self.SetxTickState())
        self.xTickToggle.state(['!alternate'])
        self.xTickToggle.state(['!selected'])
        self.xTickToggle.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        yTickTogglelbl = Label(self, text="Specify y-axis ticks:")
        yTickTogglelbl.grid(sticky=W, row=gridcounter, column=0)
        self.yTickToggle = ttk.Checkbutton(self, command=lambda: self.SetyTickState())
        self.yTickToggle.state(['!alternate'])
        self.yTickToggle.state(['!selected'])
        self.yTickToggle.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        xMjTicklbl = Label(self, text="x- major/minor tick interval:")
        xMjTicklbl.grid(sticky=W, row=gridcounter, column=0)
        self.xMjTick = Entry(self, width=3)
        self.xMjTick.grid(sticky=W, row=gridcounter, column=1)
        self.xMjTick.insert(10, "10")
        self.xMjTick.config(state=DISABLED)
        xMjTicklbl2 = Label(self, text="/", anchor=W, justify=LEFT)
        xMjTicklbl2.grid(sticky=W, row=gridcounter, column=2)
        self.xMiTick = Entry(self, width=3)
        self.xMiTick.grid(sticky=W, row=gridcounter, column=3)
        self.xMiTick.insert(5, "5")
        self.xMiTick.config(state=DISABLED)
        gridcounter += 1

        yMjTicklbl = Label(self, text="y- major/minor tick interval:")
        yMjTicklbl.grid(sticky=W, row=gridcounter, column=0)
        self.yMjTick = Entry(self, width=5)
        self.yMjTick.grid(sticky=W, row=gridcounter, column=1)
        self.yMjTick.insert(1000, "1000")
        self.yMjTick.config(state=DISABLED)
        yMjTicklbl2 = Label(self, text="/", anchor=W, justify=LEFT)
        yMjTicklbl2.grid(sticky=W, row=gridcounter, column=2)
        self.yMiTick = Entry(self, width=5)
        self.yMiTick.grid(sticky=W, row=gridcounter, column=3)
        self.yMiTick.insert(500, "500")
        self.yMiTick.config(state=DISABLED)
        gridcounter += 1

        ticksButtonlbl = Label(self, text="Show hkl ticks:")
        ticksButtonlbl.grid(sticky=W, row=gridcounter, column=0)
        self.ticksButton = ttk.Checkbutton(self, command=lambda: StartPage.hklToggle(self))
        self.ticksButton.grid(sticky=W, row=gridcounter, column=1)
        if Graph.hkl_loaded == 1:
            self.ticksButton.state(['!alternate'])
            self.ticksButton.state(['selected'])
        else:
            self.ticksButton.configure(state=DISABLED)
        gridcounter += 1

        ticksoffsetlbl = Label(self, text="hkl ticks offset:")
        ticksoffsetlbl.grid(sticky=W, row=gridcounter, column=0)
        self.ticksButtonOffset = ttk.Entry(self, width=5)
        self.ticksButtonOffset.insert(-40, "-40")
        self.ticksButtonOffset.grid(sticky=W, row=gridcounter, column=1)
        if Graph.hkl_loaded == 1:
            self.ticksButtonOffset.state(['!alternate'])
            self.ticksButtonOffset.state(['selected'])
        else:
            self.ticksButtonOffset.configure(state=DISABLED)
        gridcounter += 1

        DiffCurveButtonlbl = Label(self, text="Show difference curve:")
        DiffCurveButtonlbl.grid(sticky=W, row=gridcounter, column=0)
        self.DiffCurveButton = ttk.Checkbutton(self, command=lambda: StartPage.SetDiffCurvState(self))
        self.DiffCurveButton.state(['!alternate'])
        self.DiffCurveButton.state(['selected'])
        self.DiffCurveButton.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        DiffCurveOffsetlbl = Label(self, text="Difference Curve offset:")
        DiffCurveOffsetlbl.grid(sticky=W, row=gridcounter, column=0)
        self.DiffCurveOffset = ttk.Entry(self, width=5)
        self.DiffCurveOffset.insert(-500, "-500")
        self.DiffCurveOffset.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

    # this stuff takes care of setting up the legend. Location etc #
        LegendLocater = ttk.Menubutton(self, text="Legend Position")
        LegendLocater.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        LegendLocater.menu = Menu(LegendLocater, tearoff=0)
        LegendLocater["menu"] = LegendLocater.menu
        self.LegendTopRight = tk.IntVar()
        self.LegendTopLeft = tk.IntVar()
        self.LegendBotLeft = tk.IntVar()
        self.LegendBotRight = tk.IntVar()
        self.LegendOff = tk.IntVar()

        LegendLocater.menu.add_checkbutton(label="Top right", variable=self.LegendTopRight, command=lambda: StartPage.LegendTR(self))
        LegendLocater.menu.add_checkbutton(label="Top left", variable=self.LegendTopLeft, command=lambda: StartPage.LegendTL(self))
        LegendLocater.menu.add_checkbutton(label="Bottom right",variable=self.LegendBotRight, command=lambda: StartPage.LegendBR(self))
        LegendLocater.menu.add_checkbutton(label="Bottom left", variable=self.LegendBotLeft, command=lambda: StartPage.LegendBL(self))
        LegendLocater.menu.add_checkbutton(label="Turn legend off", variable=self.LegendOff, command=lambda: StartPage.LegendLO(self))
        gridcounter += 1

        LegendTextSizelbl = Label(self, text="Legend text size:")
        LegendTextSizelbl.grid(sticky=W, row=gridcounter, column=0)
        self.LegendTextSize = Entry(self, width=3)
        self.LegendTextSize.grid(sticky=W, row=gridcounter, column=1)
        self.LegendTextSize.insert(18, "18")
        gridcounter += 1

        self.UpdateGraph = ttk.Button(self, text="Update graph", command=lambda: StartPage.LoadGraph(self))
        self.UpdateGraph.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        if self.NoFileChecker == 0:
            self.UpdateGraph.configure(state=DISABLED)
        else:
            self.UpdateGraph.configure(state=NORMAL)
        gridcounter += 1

        SaveFig = ttk.Button(self, text="Save figure", command=lambda: StartPage.saveFigFunc(self))
        SaveFig.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        gridcounter += 1

        dialoguelbl = Label(self, text="Datasets currently open:")
        dialoguelbl.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        gridcounter += 1

        self.gridcounter2 = gridcounter
        dialoguelbl = Label(self, text=StartPage.dialogueBox(self))
        dialoguelbl.grid(sticky=NW, row=self.gridcounter2, column=0, pady=4, padx=4, columnspan=2)
        gridcounter += 1

    def dialogueBox(self):
        if self.NoFileChecker == 0:
            self.datasetString = str("No datasets loaded.")
            return self.datasetString
        else:
            self.datasetString = str(path.basename(self.TopasFile))
            dialoguelbl = Label(self, text=self.datasetString)
            dialoguelbl.grid(sticky=NW, row=self.gridcounter2, column=0, pady=4, padx=4, columnspan=2)
            return self.datasetString

    def CheckGraphCounter(self):
        print(self.GraphCount)
        self.GraphCount = self.GraphCount

    def LegendTR(self):
        self.LegendTopLeft.set(0)
        self.LegendBotLeft.set(0)
        self.LegendBotRight.set(0)
        self.LegendOff.set(0)
        self.legLoc = 'upper right'  # location of the legend
        self.LegendBool = 0

    def LegendTL(self):
        self.LegendTopRight.set(0)
        self.LegendBotLeft.set(0)
        self.LegendBotRight.set(0)
        self.LegendOff.set(0)
        self.legLoc = 'upper left'  # location of the legend
        self.LegendBool = 0

    def LegendBR(self):
        self.LegendTopLeft.set(0)
        self.LegendTopRight.set(0)
        self.LegendBotLeft.set(0)
        self.LegendOff.set(0)
        self.legLoc = 'lower right'  # location of the legend
        self.LegendBool = 0

    def LegendBL(self):
        self.LegendTopLeft.set(0)
        self.LegendTopRight.set(0)
        self.LegendBotRight.set(0)
        self.LegendOff.set(0)
        self.legLoc = 'lower left'  # location of the legend
        self.LegendBool = 0

    def LegendLO(self):
        self.LegendTopLeft.set(0)
        self.LegendTopRight.set(0)
        self.LegendBotLeft.set(0)
        self.LegendBotRight.set(0)
        self.LegendBool = 1

    def LoadGraph(self):
        #setup the graphical elements; fonts, colors, etc
        matplotlib.rc('font', size=self.allSized, **{'family': "arial"})  # controls default text sizes
        matplotlib.rc('axes', titlesize=self.allSized)  # fontsize of the axes title
        matplotlib.rc('axes', labelsize=self.allSized)  # fontsize of the x and y labels
        matplotlib.rc('xtick', labelsize=self.allSized)  # fontsize of the tick labels
        matplotlib.rc('ytick', labelsize=self.allSized)  # fontsize of the tick labels
        matplotlib.rc('legend', fontsize=self.allSized)  # legend fontsize
        matplotlib.rc('figure', titlesize=self.allSized)  # fontsize of the figure title
        self.diffColor = "blue"
        self.fitColor = "red"
        self.dataColor = "black"
        self.arr_graph = np.loadtxt(self.TopasFile, delimiter=',', dtype='float', skiprows=self.rowSkip - 1,
                                    unpack=True)
        self.f = Figure(figsize=(6, 6), dpi=100)
        self.ax1 = self.f.add_subplot(111)
        self.ax1.set_ylabel('Intensity (Counts)')
        self.ax1.set_xlabel('2$\Theta$ ($^\circ$, CuK$_{\\alpha}$)')
        if self.x_col:
            if self.raw_col:
                self.ax1.plot(self.arr_graph[int(self.x_col_loc)], self.arr_graph[1],
                              color=self.dataColor, marker='o', lineStyle='None', label='Data', markersize=4)
            else:
                print("there is no raw data")
            if self.ycalc_col:
                self.ax1.plot(self.arr_graph[int(self.x_col_loc)], self.arr_graph[int(self.ycalc_col_loc)],
                              color=self.fitColor, lineStyle='-', label='Calculated')
            else:
                print("there is no ycalc data")
            if self.diff_col:

                if Graph.hkl_loaded == 1 & self.ticksButton.instate(['selected']):
                    self.maxDiff = np.max(self.arr_graph[int(self.diff_col_loc)])
                else:
                    self.maxDiff = np.max(self.arr_graph[int(self.diff_col_loc)])
                a = self.ax1.plot(self.arr_graph[int(self.x_col_loc)], self.arr_graph[int(self.diff_col_loc)] - self.maxDiff,
                              color=self.diffColor, lineStyle='-', label='Difference')

            else:
                print("there is no diff data")
        else:
            print("there is no x-axis data")

        if Graph.hkl_loaded == 1 and self.ticksButton.instate(['selected']):
            print("graph.hkl_loaded is:")
            print(Graph.hkl_loaded)
            self.ax1.plot(self.arr_hkl, (self.arr_hkl - self.arr_hkl) + int(self.ticksButtonOffset.get()),
                          color=self.fitColor, marker='|', label='hkl phase', linestyle='None', markerSize=20)
        else:
            pass
            print("misses the iff to here")
            print(Graph.hkl_loaded)

        if self.firstGraphPlot == 0: #run this code to setup the initial graph
            self.ax1.xaxis.set_major_locator(ticker.AutoLocator())  # when first plotted, will use autolocator.
            self.ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator())  # when first plotted, will use autolocator.
        else: #run this code to update graph
            #self.f = Figure(figsize=(6, 6), dpi=100)
            # self.f.autolayout: True
            #self.ax1 = self.f.add_subplot(111)
            self.xRangeLowValue = int(self.xRangeLow.get())
            self.xRangeHighValue = int(self.xRangeHigh.get())
            self.yRangeLowValue = int(self.yRangeLow.get())
            self.yRangeHighValue = int(self.yRangeHigh.get())
            self.DiffCurveOffsetValue = int(self.DiffCurveOffset.get())

            if self.diff_col:
                for handle in a: #removes the current diff curve as this function moves it based on the following
                    handle.remove()

                if self.DiffCurveButton.instate(['selected']) == TRUE: # checks if show diff is true
                    a = self.ax1.plot(self.arr_graph[int(self.x_col_loc)], # plots curve based on offset value
                                           (self.arr_graph[int(self.diff_col_loc)]+self.DiffCurveOffsetValue),
                                           color=self.diffColor, lineStyle='-', label='Difference')
                    print(self.DiffCurveOffsetValue)
                else:
                    print("curve has been deleted") # code w/ handle above has already deleted line, so just pass
            self.ax1.set_xlim(self.xRangeLowValue, self.xRangeHighValue)
            self.ax1.set_ylim(self.yRangeLowValue, self.yRangeHighValue)
            if self.xTickToggle.instate(['selected']) == TRUE:
                self.ax1.xaxis.set_major_locator(ticker.MultipleLocator(float(self.xMjTick.get())))
                self.ax1.xaxis.set_minor_locator(ticker.MultipleLocator(float(self.xMiTick.get())))
            else:
                self.ax1.xaxis.set_major_locator(ticker.AutoLocator())
                self.ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator())

            if self.yTickToggle.instate(['selected']) == TRUE:
                self.ax1.yaxis.set_major_locator(ticker.MultipleLocator(float(self.yMjTick.get())))
                self.ax1.yaxis.set_minor_locator(ticker.MultipleLocator(float(self.yMiTick.get())))
            else:
                self.ax1.yaxis.set_major_locator(ticker.AutoLocator())
                self.ax1.yaxis.set_minor_locator(ticker.AutoMinorLocator())

        if self.LegendBool == 1:
            self.ax1.legend().remove()
        else:
            self.ax1.legend(loc=self.legLoc, prop={'size': self.LegendTextSize.get()}, frameon=False, bbox_transform=plt.gcf().transFigure)

        canvas = FigureCanvasTkAgg(self.f, self)
        canvas.draw()
        canvas._tkcanvas.grid(row=0, column=3, columnspan=1000, rowspan=1000, padx=50, pady=5)
        self.firstGraphPlot = 1  # this makes sure you will only update the plot from now on using the following
        print("can you plot")

    def hklToggle(self):
        if self.ticksButton.instate(['selected']):
            self.ticksButtonOffset.config(state=NORMAL)
        elif self.ticksButton.instate(['!selected']):
            self.ticksButtonOffset.config(state=DISABLED)


    def SetxTickState(self):
        if self.xTickToggle.instate(['selected']):
            self.xMjTick.config(state=NORMAL)
            self.xMiTick.config(state=NORMAL)

        elif self.xTickToggle.instate(['!selected']):
            self.xMjTick.config(state=DISABLED)
            self.xMiTick.config(state=DISABLED)

    def SetyTickState(self):
        if self.yTickToggle.instate(['selected']):
            self.yMjTick.config(state=NORMAL)
            self.yMiTick.config(state=NORMAL)

        elif self.yTickToggle.instate(['!selected']):
            self.yMjTick.config(state=DISABLED)
            self.yMiTick.config(state=DISABLED)

    def SetDiffCurvState(self):
        if self.DiffCurveButton.instate(['selected']):
            self.DiffCurveOffset.config(state=NORMAL)
        elif self.DiffCurveButton.instate(['!selected']):
            self.DiffCurveOffset.config(state=DISABLED)

    def saveFigFunc(self):
        self.SaveFig = filedialog.asksaveasfilename(initialdir="/", title="save figure name:",
                                                filetypes=(("png", "*.png"), ("all files", "*.*")))
        self.f.savefig(self.SaveFig, dpi=300, facecolor='white', bbox_inches='tight')

    def initiateGraph(self):

        if self.graphCounter == 0:
            # graph_1.LoadGraph()
            graph_1 = Graph()
            graph_1.fileOpen()
            self.graphCounter = 1
        elif graphCounter == 1:
            graph_2 = Graph()
            graph_2()
            self.graphCounter = 2
        elif graphCounter == 2:
            graph_3 = Graph()
            graph_3()
            self.graphCounter = 3
        elif graphCounter == 3:
            graph_4 = Graph()
            graph_4()
            self.graphCounter = 4






class GraphTemplateFrame(tk.Frame):
    def __init__(self, parent, controller): # setup the layout of the page
        tk.Frame.__init__(self, parent)
        counter = 0

        GraphPageButton = ttk.Button(self, text="Return to graph page", command=lambda: controller.show_frame(StartPage))
        GraphPageButton.grid(sticky=NW, row=counter, column=0, pady=4, padx=4)
        counter += 1

        GraphLayoutlabel = Label(self, text="Please select a graphical layout.")
        GraphLayoutlabel.grid(sticky=W+N, row=counter, column=0)
        counter += 1

        self.var = IntVar()
        self.var.set(1)
        self.Graphhklcombined = ttk.Radiobutton(self, text="combined ticks and data", variable=self.var, value=1)
        self.Graphhklcombined.grid(sticky=W+N, row=counter, column=0)
        counter += 1

        self.GraphhklSeparated = ttk.Radiobutton(self, text="Separated ticks & data", variable=self.var, value=2)
        self.GraphhklSeparated.grid(sticky=W+N, row=counter, column=0)
        counter += 1


        self.fig = plt.figure(figsize=(3, 3))
        self.hkl_tick_file_count = 1
        gs = self.fig.add_gridspec(2, 1, height_ratios=[self.hkl_tick_file_count, 20])
        gs.update(wspace=0.025, hspace=0.025)  # set the spacing between axes.
        ax1 = self.fig.add_subplot(gs[0, :])
        ax2 = self.fig.add_subplot(gs[1:, :])
        ax2.text(0.5, 0.5, 'separated ticks & data', ha='center', va='center', size=16, alpha=.75)

        inner_grid = gridspec.GridSpecFromSubplotSpec(self.hkl_tick_file_count, 1, subplot_spec=gs[0], hspace=0,
                                                      wspace=0.0)  # , hspace=1)

        for i in range(self.hkl_tick_file_count):
            ax3 = plt.subplot(inner_grid[i])
            ax3.tick_params(axis='x', direction='in', top=False, bottom=False, labeltop=False, labelbottom=False)
            ax3.tick_params(axis='y', direction='in', left=False, right=False, labelleft=False, labelright=False)
            ax3.text(0.5, 0.5, 'hkl ticks', ha='center', va='center', size=6, alpha=.75, fontweight='bold')

        ax1.tick_params(axis='x', direction='in', top=False, bottom=False, labeltop=False, labelbottom=False)
        ax1.tick_params(axis='y', direction='in', left=False, right=False, labelleft=False, labelright=False)
        ax2.tick_params(axis='x', direction='in', top=True, bottom=True, labeltop=False, labelbottom=False)
        ax2.tick_params(axis='y', direction='in', left=True, right=True, labelleft=False, labelright=False)       # ax1 = plt.subplot(gs[0])
        canvas = FigureCanvasTkAgg(self.fig, self)
        canvas.draw()
        #canvas._tkcanvas.grid(row=1, column=21, columnspan=1000, rowspan=1000, padx=50, pady=5)
        canvas._tkcanvas.grid(row=3, column=3, padx=50, pady=5)


        self.fig2 = plt.figure(figsize=(3, 3))
        hkl_tick_file_count = 1
        ax1 = self.fig2.add_subplot(111)

        ax1.tick_params(axis='x', direction='in', top=True, bottom=True, labeltop=False, labelbottom=False)
        ax1.tick_params(axis='y', direction='in', left=True, right=True, labelleft=False, labelright=False)
        ax1.text(0.5, 0.5, 'Combined hkl & data', ha='center', va='center', size=16, alpha=.75)

        canvas2 = FigureCanvasTkAgg(self.fig2, self)
        canvas2.draw()
        canvas2._tkcanvas.grid(row=3, column=2, padx=50, pady=5)

        #  setup the other graph option




app = IoPlot()
app.geometry("1000x600")
app.resizable(width=False, height=False)
app.mainloop()
