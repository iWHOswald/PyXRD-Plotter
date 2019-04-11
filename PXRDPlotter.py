from os import path
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from scipy.optimize import leastsq
from matplotlib import gridspec
from pylab import * #imports matplotlib (and ???)
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

minor_locator = AutoMinorLocator(2)
matplotlib.rcParams.update({'figure.autolayout': True})


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



class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        def fileOpen(self):
            self.TopasFile = filedialog.askopenfilename(initialdir="/", title="Select TOPAS file",
                                                   filetypes=(("TOPAS files", "*.txt"), ("all files", "*.*")))
            self.winfo_toplevel().title("PXRD Plotter - current file: " + path.basename(self.TopasFile))
            LoadGraph(self)

        def LoadGraph(self):
            t, data, diff, fit = np.loadtxt(self.TopasFile, delimiter=',', dtype='float', skiprows=2, unpack=True)
            self.f = Figure(figsize=(6, 6), dpi=100)
            ax1 = self.f.add_subplot(111)
            ax1.plot(t, data, color=dataColor, marker='o', lineStyle='None', label='Data', markersize=4)
            ax1.plot(t, fit, color=fitColor, label='Fit')
            ax1.plot(t, diff, color=diffColor, label="Difference")
            ax1.set_ylabel('Intensity (Counts)')
            ax1.set_xlabel('2$\Theta$ ($^\circ$, CuK$_{\\alpha}$)')
            ax1.xaxis.set_minor_locator(minor_locator)
            ax1.yaxis.set_minor_locator(minor_locator)

            ax1.legend(loc=legLoc, frameon=False, bbox_transform=plt.gcf().transFigure)
            canvas = FigureCanvasTkAgg(self.f, self)
            canvas.draw()
            canvas._tkcanvas.grid(row=0, column=3, columnspan=1000, rowspan=1000, padx=50, pady=5)

        upload_button = ttk.Button(self, text="Open TOPAS file",command=lambda: fileOpen(self))
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
        yRangeHigh.insert(5000, "5000")

        ticksButtonlbl = Label(self, text="Show hkl ticks:")
        ticksButtonlbl.grid(sticky=W, row=4, column=0)
        ticksButton = ttk.Checkbutton(self)

        ticksButton.grid(sticky=W, row=4, column=1)



        DiffCurveButtonlbl = Label(self, text="Show diff curve:")
        DiffCurveButtonlbl.grid(sticky=W, row=5, column=0)
        DiffCurveButton = ttk.Checkbutton(self, command=lambda: SetDiffCurvState())
        DiffCurveButton.state(['!alternate'])
        DiffCurveButton.state(['selected'])
        DiffCurveButton.grid(sticky=W, row=5, column=1)

        def SetDiffCurvState():
            if DiffCurveButton.instate(['selected']):
                DiffCurveOffset.config(state=NORMAL)
            elif DiffCurveButton.instate(['!selected']):
                DiffCurveOffset.config(state=DISABLED)

        DiffCurveOffsetlbl = Label(self, text="Diff Curve offset:")
        DiffCurveOffsetlbl.grid(sticky=W, row=6, column=0)
        DiffCurveOffset = ttk.Entry(self, width=5)
        DiffCurveOffset.insert(-500, "500")
        DiffCurveOffset.grid(sticky=W, row=6, column=1)
        ChangeLayout = ttk.Button(self, text="Change layout",
                        command=lambda: filedialog.askopenfilename(initialdir="/", title="Select file",
                                                   filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*"))))
        ChangeLayout.grid(sticky=NW, row=7, column=0, pady=4, padx=4)

        def updateGraphfunc(self):
            xRangeLowValue = int(xRangeLow.get())
            xRangeHighValue = int(xRangeHigh.get())
            yRangeLowValue = int(yRangeLow.get())
            yRangeHighValue = int(yRangeHigh.get())
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
            ax1.set_xlim(xRangeLowValue, xRangeHighValue)
            ax1.set_ylim(yRangeLowValue, yRangeHighValue)
            ax1.xaxis.set_minor_locator(minor_locator)
            ax1.yaxis.set_minor_locator(minor_locator)
            ax1.legend(loc=legLoc, frameon=False, bbox_transform=plt.gcf().transFigure)
            canvas = FigureCanvasTkAgg(self.f, self)
            canvas.draw()
            canvas._tkcanvas.grid(row=0, column=3, columnspan=1000, rowspan=1000, padx=50, pady=5)

        def saveFigFunc(self):
            self.SaveFig = filedialog.asksaveasfilename(initialdir="/", title="save figure name:",
                                                    filetypes=(("png", "*.png"), ("all files", "*.*")))
            self.f.savefig(self.SaveFig, dpi=300, facecolor='white', bbox_inches='tight')

        UpdateGraph = ttk.Button(self, text="Update graph", command=lambda:updateGraphfunc(self))
        UpdateGraph.grid(sticky=NW, row=8, column=0, pady=4, padx=4)

        SaveFig = ttk.Button(self, text="Save figure", command=lambda: saveFigFunc(self))
        SaveFig.grid(sticky=NW, row=9, column=0, pady=4, padx=4)


        dataColor = 'k'  # black
        fitColor = 'tab:blue'
        diffColor = 'tab:orange'
        legLoc = 'upper right'  # location of the legend in the center box
        matplotlib.rc('font', **{'family': "arial"})

        allSized = 18  # Whatever you want all the text size to be.
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









