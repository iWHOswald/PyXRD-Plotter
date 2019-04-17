from os import path
import numpy as np
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import matplotlib
import matplotlib.ticker as ticker
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pylab import * #imports matplotlib (and ???)
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)


minor_locator = AutoMinorLocator(2)
matplotlib.rcParams.update({'figure.autolayout': True})
dataColor = 'k'  # black
fitColor = 'tab:blue'
diffColor = 'tab:orange'
legLoc = 'upper right'  # location of the legend in the center box
matplotlib.rc('font', **{'family': "arial"})
allSized = 18  # Whatever you want all the text size to be.


# python 3 app
class IoPlot(tk.Tk):   # IoPlot will inherit attributes from the tkinter module. the (tk.TK) is not technically necesary


    def __init__(self, *args, **kwargs):  # this is here to always load the following. always run when IoPlot is called
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "PXRD Plotter")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=0)
        container.grid_columnconfigure(0, weight=0)

        self.frames = {}
        frame = StartPage(container, self)
        self.frames[StartPage] = frame

        frame.grid(row=10, column=10, sticky="nsew")
        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class Graph:

    def __init__(self, x, raw, sigmayobs, diff, ycalc):
        self.x = x
        self.raw = raw
        self.sigmayobs = sigmayobs
        self.diff = diff
        self.ycalc = ycalc

    def fileOpen(self):
        self.TopasFile = filedialog.askopenfilename(initialdir="/", title="Select TOPAS file",
                                               filetypes=(("TOPAS files", "*.txt"), ("all files", "*.*")))
        self.winfo_toplevel().title("PXRD Plotter - current file: " + path.basename(self.TopasFile))

        self.rowSkip = 1

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
            print(arr)
            print(np.size(arr))
            self.column_count = np.size(arr)
            counter = 4

            for columns in range(self.column_count):
                print(arr[self.column_count-counter:self.column_count-counter+1])
                counter -= 1

            if np.where(arr == "'x"):
                self.x_col = True
                a = str(np.where(arr == "'x")).isdigit()
                print(a)

            else:
                self.x_col = False

            if np.where(arr == "Diff"):
                self.diff_col = True
                self.diffColor = "blue"

            else:
                self.diff_col = False

            if np.where(arr == "Ycalc"):
                self.ycalc_col = True
            else:
                self.ycalc_col = False

            if arr[1:2] != "'x" and arr[1:2] != "Diff" and arr[1:2] != "Ycalc" and arr[1:2] != "Bkg":
                self.raw_col = True
            else:
                self.raw_col = False

            if np.where(arr == "Bkg"):
                self.bkg_col = True
            else:
                self.bkg_col = False

            if np.where(arr == "xy_cumchi2"):
                self.cumchi2_col = True
            else:
                self.cumchi2_col = False
        Graph.LoadGraph(self)

    def LoadGraph(self):

        arr_graph = np.loadtxt(self.TopasFile, delimiter=',', dtype='float', skiprows=self.rowSkip-1,
                                        unpack=True)
        self.f = Figure(figsize=(6, 6), dpi=100)
        ax1 = self.f.add_subplot(111)
        counter = 1
        for all_columns in range(self.column_count - 1):
            if self.x_col:
                ax1.plot(arr_graph[0], arr_graph[1],
                         color=dataColor, marker='o', lineStyle='None', label='Data', markersize=4)
            else:
                print("there is no x-axis data")



            counter += 1
            #ax1.plot(t, fit, color=fitColor, label='Fit')
            #ax1.plot(t, diff, color=diffColor, label="Difference")
        ax1.set_ylabel('Intensity (Counts)')
        ax1.set_xlabel('2$\Theta$ ($^\circ$, CuK$_{\\alpha}$)')
        ax1.xaxis.set_major_locator(ticker.AutoLocator())
        ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator())

        ax1.legend(loc=legLoc, frameon=False, bbox_transform=plt.gcf().transFigure)
        canvas = FigureCanvasTkAgg(self.f, self)
        canvas.draw()
        canvas._tkcanvas.grid(row=0, column=3, columnspan=1000, rowspan=1000, padx=50, pady=5)









class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


        upload_button = ttk.Button(self, text="Open TOPAS file",command=lambda: Graph.fileOpen(self))
        upload_button.grid(sticky=NW, row=0, column=0, pady=4, padx=4)
        formatLabel = Label(self, text="Graph settings")
        formatLabel.grid(sticky=W, row=1, column=0)
        xRange = Label(self, text="x-axis range (2theta):")
        xRange.grid(sticky=W, row=2, column=0)
        xRangeLow = Entry(self, width=3)
        xRangeLow.insert(5, "5")
        xRangeLow.grid(sticky=W, row=2, column=1)
        xRangeTo = Label(self, text="to")
        xRangeTo.grid(sticky=W, row=2, column=2)
        xRangeHigh = Entry(self, width=3)
        xRangeHigh.insert(50, "50")
        xRangeHigh.grid(sticky=W, row=2, column=3)

        yRange = Label(self, text="y-axis range (intensity):")
        yRange.grid(sticky=W, row=3, column=0)
        yRangeLow = Entry(self, width=5)
        yRangeLow.grid(sticky=W, row=3, column=1)
        yRangeLow.insert(-2000, "-2000")
        yRange = Label(self, text="to", anchor=W, justify=LEFT)
        yRange.grid(sticky=W, row=3, column=2)
        yRangeHigh = Entry(self, width=5)
        yRangeHigh.grid(sticky=W, row=3, column=3)
        yRangeHigh.insert(6000, "6000")

        xTickTogglelbl = Label(self, text="Specify x-axis ticks:")
        xTickTogglelbl.grid(sticky=W, row=4, column=0)
        xTickToggle = ttk.Checkbutton(self, command=lambda: SetxTickState())
        xTickToggle.state(['!alternate'])
        xTickToggle.state(['!selected'])
        xTickToggle.grid(sticky=W, row=4, column=1)

        yTickTogglelbl = Label(self, text="Specify y-axis ticks:")
        yTickTogglelbl.grid(sticky=W, row=5, column=0)
        yTickToggle = ttk.Checkbutton(self, command=lambda: SetyTickState())
        yTickToggle.state(['!alternate'])
        yTickToggle.state(['!selected'])
        yTickToggle.grid(sticky=W, row=5, column=1)

        def SetxTickState():
            if xTickToggle.instate(['selected']):
                xMjTick.config(state=NORMAL)
                xMiTick.config(state=NORMAL)

            elif xTickToggle.instate(['!selected']):
                xMjTick.config(state=DISABLED)
                xMiTick.config(state=DISABLED)


        xMjTicklbl = Label(self, text="x- major/minor tick interval:")
        xMjTicklbl.grid(sticky=W, row=6, column=0)
        xMjTick = Entry(self, width=3)
        xMjTick.grid(sticky=W, row=6, column=1)
        xMjTick.insert(10, "10")
        xMjTick.config(state=DISABLED)
        xMjTicklbl2 = Label(self, text="/", anchor=W, justify=LEFT)
        xMjTicklbl2.grid(sticky=W, row=6, column=2)
        xMiTick = Entry(self, width=3)
        xMiTick.grid(sticky=W, row=6, column=3)
        xMiTick.insert(5, "5")
        xMiTick.config(state=DISABLED)






        def SetyTickState():
            if yTickToggle.instate(['selected']):
                yMjTick.config(state=NORMAL)
                yMiTick.config(state=NORMAL)

            elif yTickToggle.instate(['!selected']):
                yMjTick.config(state=DISABLED)
                yMiTick.config(state=DISABLED)

        yMjTicklbl = Label(self, text="y- major/minor tick interval:")
        yMjTicklbl.grid(sticky=W, row=7, column=0)
        yMjTick = Entry(self, width=5)
        yMjTick.grid(sticky=W, row=7, column=1)
        yMjTick.insert(1000, "1000")
        yMjTick.config(state=DISABLED)
        yMjTicklbl2 = Label(self, text="/", anchor=W, justify=LEFT)
        yMjTicklbl2.grid(sticky=W, row=7, column=2)
        yMiTick = Entry(self, width=5)
        yMiTick.grid(sticky=W, row=7, column=3)
        yMiTick.insert(500, "500")
        yMiTick.config(state=DISABLED)

        ticksButtonlbl = Label(self, text="Show hkl ticks:")
        ticksButtonlbl.grid(sticky=W, row=8, column=0)
        ticksButton = ttk.Checkbutton(self)
        ticksButton.grid(sticky=W, row=8, column=1)

        DiffCurveButtonlbl = Label(self, text="Show diff curve:")
        DiffCurveButtonlbl.grid(sticky=W, row=9, column=0)
        DiffCurveButton = ttk.Checkbutton(self, command=lambda: SetDiffCurvState())
        DiffCurveButton.state(['!alternate'])
        DiffCurveButton.state(['selected'])
        DiffCurveButton.grid(sticky=W, row=9, column=1)

        def SetDiffCurvState():
            if DiffCurveButton.instate(['selected']):
                DiffCurveOffset.config(state=NORMAL)
            elif DiffCurveButton.instate(['!selected']):
                DiffCurveOffset.config(state=DISABLED)

        DiffCurveOffsetlbl = Label(self, text="Diff Curve offset:")
        DiffCurveOffsetlbl.grid(sticky=W, row=10, column=0)
        DiffCurveOffset = ttk.Entry(self, width=5)
        DiffCurveOffset.insert(-500, "-500")
        DiffCurveOffset.grid(sticky=W, row=10, column=1)

        ChangeLayout = ttk.Button(self, text="Change layout",
                        command=lambda: filedialog.askopenfilename(initialdir="/", title="Select file",
                                                   filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*"))))
        ChangeLayout.grid(sticky=NW, row=11, column=0, pady=4, padx=4)

        def updateGraphfunc(self):
            self.xRangeLowValue = int(xRangeLow.get())
            self.xRangeHighValue = int(xRangeHigh.get())
            self.yRangeLowValue = int(yRangeLow.get())
            self.yRangeHighValue = int(yRangeHigh.get())
            DiffCurveOffsetValue = int(DiffCurveOffset.get())

            t, data, diff, fit = np.loadtxt(self.TopasFile, delimiter=',', dtype='float', skiprows=2, unpack=True)
            self.f = Figure(figsize=(6, 6), dpi=100)
            self.f.autolayout: True
            ax1 = self.f.add_subplot(111)
            ax1.plot(t, data, color=dataColor, marker='o', lineStyle='None', label='Data', markersize=4)
            ax1.plot(t, fit, color=fitColor, label='Fit')
            if DiffCurveButton.instate(['selected']) == TRUE:
                ax1.plot(t, diff + DiffCurveOffsetValue, color=diffColor, label="Difference")
                print(DiffCurveOffsetValue)
            else:
                ax1.plot(t, diff - 900000, color=diffColor, label="Difference")

            ax1.set_ylabel('Intensity (Counts)')
            ax1.set_xlabel('2$\Theta$ ($^\circ$, CuK$_{\\alpha}$)')
            ax1.set_xlim(self.xRangeLowValue, self.xRangeHighValue)
            ax1.set_ylim(self.yRangeLowValue, self.yRangeHighValue)
            if xTickToggle.instate(['selected']) == TRUE:
                ax1.xaxis.set_major_locator(ticker.MultipleLocator(float(xMjTick.get())))
                ax1.xaxis.set_minor_locator(ticker.MultipleLocator(float(xMiTick.get())))
            else:
                ax1.xaxis.set_major_locator(ticker.AutoLocator())
                ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator())

            if yTickToggle.instate(['selected']) == TRUE:
                ax1.yaxis.set_major_locator(ticker.MultipleLocator(float(yMjTick.get())))
                ax1.yaxis.set_minor_locator(ticker.MultipleLocator(float(yMiTick.get())))
            else:
                ax1.yaxis.set_major_locator(ticker.AutoLocator())
                ax1.yaxis.set_minor_locator(ticker.AutoMinorLocator())

            ax1.legend(loc=legLoc, frameon=False, bbox_transform=plt.gcf().transFigure)
            canvas = FigureCanvasTkAgg(self.f, self)
            canvas.draw()
            canvas._tkcanvas.grid(row=0, column=3, columnspan=1000, rowspan=1000, padx=50, pady=5)

        def saveFigFunc(self):
            self.SaveFig = filedialog.asksaveasfilename(initialdir="/", title="save figure name:",
                                                    filetypes=(("png", "*.png"), ("all files", "*.*")))
            self.f.savefig(self.SaveFig, dpi=300, facecolor='white', bbox_inches='tight')

        UpdateGraph = ttk.Button(self, text="Update graph", command=lambda:updateGraphfunc(self))
        UpdateGraph.grid(sticky=NW, row=12, column=0, pady=4, padx=4)

        SaveFig = ttk.Button(self, text="Save figure", command=lambda: saveFigFunc(self))
        SaveFig.grid(sticky=NW, row=13, column=0, pady=4, padx=4)





        matplotlib.rc('font', size=allSized, **{'family': "arial"})  # controls default text sizes
        matplotlib.rc('axes', titlesize=allSized)  # fontsize of the axes title
        matplotlib.rc('axes', labelsize=allSized)  # fontsize of the x and y labels
        matplotlib.rc('xtick', labelsize=allSized)  # fontsize of the tick labels
        matplotlib.rc('ytick', labelsize=allSized)  # fontsize of the tick labels
        matplotlib.rc('legend', fontsize=allSized)  # legend fontsize
        matplotlib.rc('figure', titlesize=allSized)  # fontsize of the figure title


app = IoPlot()
app.geometry("1000x600")
app.resizable(width=False, height=False)
app.mainloop()
