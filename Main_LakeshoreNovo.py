import os
#from datetime import *
import time
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import tkinter.scrolledtext as ScrolledText
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (	FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from PIL import ImageTk,Image
import numpy as np
import scipy
import scipy.constants
import threading
import pyvisa
import ResourceManage
import LakeShore336Init
import LakeShore340Init
import NovocontrolInit
import PlotMethods


class LS_Canvas_for_plots():
	def __init__(self,Frame,num_plots,**kwargs):
		self._frame = Frame
		fig, axs = plt.subplots(num_plots,figsize=(kwargs.get('width',4),kwargs.get('height',4)))
		self._fig = fig
		self._axs = axs
		'''
		#self._fig = Figure(figsize=(6,6), dpi=100)
		self._fig = plt.figure(figsize=(6,6), dpi=100)
		'''
	def initialise(self):
		canvas = FigureCanvasTkAgg(self._fig, master=self._frame)  # A tk.DrawingArea.
		toolbar = NavigationToolbar2Tk(canvas, self._frame)
		toolbar.update()
		#canvas.draw()
		canvas.get_tk_widget().pack(fill=BOTH, expand=0)
		
	
class Canvas_for_plots():
	def __init__(self,Frame,**kwargs):
		self._frame = Frame
		fig = plt.figure(figsize=(kwargs.get('width',4),kwargs.get('height',4)),constrained_layout=True)
		spec2 = gridspec.GridSpec(ncols=(kwargs.get('ncols',1)), nrows=(kwargs.get('nrows',1)), figure=fig)
		num_subplots = kwargs.get('ncols',1)*kwargs.get('nrows',1)
		axs = []
		[i,j] = [0,0]
		for n in range(num_subplots):
			[i,j] = divmod(n, kwargs.get('ncols',1))
			axs.append(fig.add_subplot(spec2[i, j]))
		self._fig = fig
		self._axs = axs

	def initialise(self):
		
		canvas = FigureCanvasTkAgg(self._fig, master=self._frame)  # A tk.DrawingArea.
		toolbar = NavigationToolbar2Tk(canvas, self._frame)
		toolbar.update()
		#canvas.draw()
		canvas.get_tk_widget().pack(fill=BOTH, expand=0)	
		 
class Curve():
	def __init__(self,Canvas,index,**kwargs):
		self._Canvas = Canvas
		self._ax = Canvas._axs[index]
		self._xData = np.empty(0)
		self._yData = np.empty(0)

		line, = self._ax.plot(self._xData, self._yData, marker=(kwargs.get("marker","o")))
		self._curve = line

	def clear(self):
		#self._ax.cla()
		self._xData = np.empty(0)
		self._yData = np.empty(0)
			

class Vari():	#create empty class for storing instances
	pass
class LSvari():	#create empty class for storing instances
	pass
class NCvari():	#create empty class for storing instances
	pass
		
	
def DataArray_initialise():
	global arrFreq,arrTemp,arrG,arrB,arrR,arrX,arrC,arrepsr1,arrepsr2,arrcond,arrrho,arrGraw,arrBraw
	arrFreq = np.empty(0)
	arrTemp = np.empty(0)
	arrG = np.empty(0)
	arrB = np.empty(0)
	arrR = np.empty(0)
	arrX = np.empty(0)
	arrC = np.empty(0)
	arrepsr1 = np.empty(0)
	arrepsr2 = np.empty(0)
	arrcond = np.empty(0)
	arrrho = np.empty(0)
	arrGraw = np.empty(0)
	arrBraw = np.empty(0)
				
def FlushMultiPlots(Curve_object_list):
	x_low = []
	x_high = []
	y_low = []
	y_high = []
	for Curve_object in Curve_object_list:
		#print("x data =: ", Curve_object._xData)
		#print("y data =: ", Curve_object._yData)
		Curve_object._curve.set_xdata(Curve_object._xData)
		x_low.append(np.min(Curve_object._xData))
		x_high.append(np.max(Curve_object._xData))
		Curve_object._curve.set_ydata(Curve_object._yData)
		y_low.append(np.min(Curve_object._yData))
		y_high.append(np.max(Curve_object._yData))
		Curve_object._Canvas._fig.canvas.flush_events()
	xmin = np.min(x_low)
	xmax = np.max(x_high)
	ymin = np.min(y_low)
	ymax = np.max(y_high)
	Curve_object_list[0]._ax.set_xlim(0.99*xmin,1.01*xmax)
	Curve_object_list[0]._ax.set_ylim(0.99*ymin,1.01*ymax)

def AddPlot(Curve_object,**kwargs):
	Curve_object._curve.set_xdata(Curve_object._xData)
	Curve_object._curve.set_ydata(Curve_object._yData)
	Curve_object._ax.set_xlim(0.99*kwargs.get('x_range')[0],1.01*kwargs.get('x_range')[1])
	Curve_object._ax.set_ylim(0.99*kwargs.get('y_range')[0],1.01*kwargs.get('y_range')[1])
	
				
def LS_EntriesInit(Frame, LSdevice_modelNo):
        global LSvars,channel,inputcurve,hrange,ramprate,rampmode,prop,inte,deri,setpt,nowtemp,houtput,dtemp_threshold,tempsd_threshold,nopts_stable

        LSvars = []

        channel = LSvari()
        setattr(channel,'name', 'channel')
        ch_na = Label(Frame, text = 'Moniter channel')
        ch_na.grid(row=3,column=0)
        setattr(channel,'value',LS.channel)
        ch_e = StringVar()
        ch_e.set(channel.value)
        ch_eh = OptionMenu(Frame,ch_e,'A','B')
        ch_eh.grid(row=3,column=1)
        setattr(channel,'entry',ch_e)
        ch_o = Label(Frame, text = LS.channel, width=8, relief=SUNKEN)
        ch_o.grid(row=3,column=2)
        setattr(channel,'olabel',ch_o)
        LSvars.append(channel)

        if LSdevice_modelNo == '340':
            inputcurve = LSvari()
            setattr(inputcurve,'name','inputcurve')
            ic_na = Label(Frame, text = 'Input curve no.')
            ic_na.grid(row=4,column=0)
            setattr(inputcurve,'value',LS.inputcurve)
            ic_e = StringVar()
            ic_e.set(inputcurve.value)
            setattr(inputcurve,'entry',ic_e)
            if channel.value == 'A':
                ic_eh = OptionMenu(Frame,ic_e,'35 [MAGNO+Amb;Cernox]','36 [DAC;Silicon]')
            elif channel.value == 'B':
                ic_eh = OptionMenu(Frame,ic_e,'42 [MAGNO;Cernox]')
            ic_eh.grid(row=4,column=1)
            setattr(inputcurve,'optionmenu',ic_eh)
            ic_o = Label(Frame, text = LS.inputcurve, width=8, relief=SUNKEN)
            ic_o.grid(row=4,column=2)
            setattr(inputcurve,'olabel',ic_o)
            LSvars.append(inputcurve)
        elif LSdevice_modelNo == '336':
            pass
            #ic_eh = OptionMenu(Frame,ic_e,'-')



        hrange = LSvari()
        setattr(hrange,'name','hrange')
        hr_na = Label(Frame, text = 'Heater range')
        hr_na.grid(row=5,column=0)
        setattr(hrange,'value',LS.hrange)
        hr_e = StringVar()
        hr_e.set(hrange.value)
        if LSdevice_modelNo == '340':
            hr_eh = OptionMenu(Frame,hr_e,'OFF', '2.5mW', '25mW', '250mW', '2.5W', '25W')
        elif LSdevice_modelNo == '336':
            hr_eh = OptionMenu(Frame,hr_e,'OFF', 'LOW', 'MED', 'HIGH')
        setattr(hrange,'optionmenu',hr_eh)
        hr_eh.grid(row=5,column=1)
        setattr(hrange,'entry',hr_e)
        hr_o = Label(Frame, text = LS.hrange, width=8, relief=SUNKEN)
        hr_o.grid(row=5,column=2)
        setattr(hrange,'olabel',hr_o)
        LSvars.append(hrange)

        ramprate = LSvari()
        setattr(ramprate,'name','ramprate')
        rr_na = Label(Frame, text = 'Ramprate (K/min)')
        rr_na.grid(row=6,column=0)
        setattr(ramprate,'value',LS.ramprate)
        rr_e = Entry(Frame,width=10,borderwidth=2)
        rr_e.insert(END, LS.ramprate)
        rr_e.grid(row=6,column=1)
        setattr(ramprate,'entry',rr_e)
        rr_o = Label(Frame, text = LS.ramprate, width=8, relief=SUNKEN)
        rr_o.grid(row=6,column=2)
        setattr(ramprate,'olabel',rr_o)
        LSvars.append(ramprate)

        rampmode = LSvari()
        setattr(rampmode,'name','rampmode')
        rmo_na = Label(Frame, text = 'Rampmode')
        rmo_na.grid(row=7,column=0)
        setattr(rampmode,'value',LS.rampmode)
        rmo_e = StringVar()
        rmo_e.set(LS.rampmode)
        rmo_eh = Checkbutton(Frame,variable=rmo_e,onvalue='1',offvalue='0')
        rmo_eh.grid(row=7,column=1)
        setattr(rampmode,'entry',rmo_e)
        rmo_o = Label(Frame, text = LS.rampmode, width=8, relief=SUNKEN)
        rmo_o.grid(row=7,column=2)
        setattr(rampmode,'olabel',rmo_o)
        LSvars.append(rampmode)

        prop = LSvari()
        setattr(prop,'name','prop')
        p_na = Label(Frame, text = 'Proportional (gain)\n[0.1 - 1000]')
        p_na.grid(row=8,column=0)
        setattr(prop,'value',LS.P)
        p_e = Entry(Frame,width=10,borderwidth=2)
        p_e.insert(END, LS.P)
        p_e.grid(row=8,column=1)
        setattr(prop,'entry',p_e)
        p_o = Label(Frame, text = LS.P, width=8, relief=SUNKEN)
        p_o.grid(row=8,column=2)
        setattr(prop,'olabel',p_o)
        LSvars.append(prop)

        inte = LSvari()
        setattr(inte,'name','inte')
        i_na = Label(Frame, text = 'Integral (reset)\n[0.1 - 1000]')
        i_na.grid(row=9,column=0)
        setattr(inte,'value',LS.I)
        i_e = Entry(Frame,width=10,borderwidth=2)
        i_e.insert(END, LS.I)
        i_e.grid(row=9,column=1)
        setattr(inte,'entry',i_e)
        i_o = Label(Frame, text = LS.I, width=8, relief=SUNKEN)
        i_o.grid(row=9,column=2)
        setattr(inte,'olabel',i_o)
        LSvars.append(inte)

        deri = LSvari()
        setattr(deri,'name','deri')
        d_na = Label(Frame, text = 'Derivative (rate)\n[0.1 - 1000]')
        d_na.grid(row=10,column=0)
        setattr(deri,'value',LS.D)
        d_e = Entry(Frame,width=10,borderwidth=2)
        d_e.insert(END, LS.D)
        d_e.grid(row=10,column=1)
        setattr(deri,'entry',d_e)
        d_o = Label(Frame, text = LS.D, width=8, relief=SUNKEN)
        d_o.grid(row=10,column=2)
        setattr(deri,'olabel',d_o)
        LSvars.append(deri)


        setpt = LSvari()
        setattr(setpt,'name', 'setpt')
        sp_na = Label(Frame, text = 'Setpoint (K)')
        sp_na.grid(row=3,column=3)
        setattr(setpt,'value',LS.setpoint)
        sp_e = Entry(Frame,width=10,borderwidth=2)
        sp_e.insert(END, LS.setpoint)
        sp_e.grid(row=3,column=4)
        setattr(setpt,'entry',sp_e)
        sp_o = Label(Frame, text = LS.setpoint, width=8, relief=SUNKEN)
        sp_o.grid(row=3,column=5)
        setattr(setpt,'olabel',sp_o)
        LSvars.append(setpt)

        nowtemp = LSvari()
        setattr(nowtemp,'name', 'nowtemp')
        nt_na = Label(Frame, text = 'Current temperature (K)')
        nt_na.grid(row=4,column=3,columnspan=2)
        setattr(nowtemp,'value',LS.nowtemp)
        nt_o = Label(Frame, text = LS.nowtemp, width=8, relief=SUNKEN)
        nt_o.grid(row=4,column=5)
        setattr(nowtemp,'olabel',nt_o)
        LSvars.append(nowtemp)

        houtput = LSvari()
        setattr(houtput,'name', 'houtput')
        ho_na = Label(Frame, text = 'Heater output (%)')
        ho_na.grid(row=5,column=3,columnspan=2)
        setattr(houtput,'value',LS.houtput)
        ho_o = Label(Frame, text = LS.houtput, width=8, relief=SUNKEN)
        ho_o.grid(row=5,column=5)
        setattr(houtput,'olabel',ho_o)
        LSvars.append(houtput)

        dtemp_threshold = LSvari()
        setattr(dtemp_threshold,'name', 'dtemp_threshold')
        dt_na = Label(Frame, text = 'delta T (K)')
        dt_na.grid(row=8,column=3)
        #setattr(dtemp_threshold,'value',0.5)
        dt_e = Entry(Frame,width=10,borderwidth=2)
        dt_e.insert(END, 0.05)
        dt_e.grid(row=8,column=4)
        setattr(dtemp_threshold,'entry',dt_e)
        dt_o = Label(Frame, text = '', width=8, relief=SUNKEN)
        dt_o.grid(row=8,column=5)
        setattr(dtemp_threshold,'olabel',dt_o)

        tempsd_threshold = LSvari()
        setattr(tempsd_threshold,'name', 'tempsd_threshold' )
        tsd_na = Label(Frame, text = 'Temp S.D.')
        tsd_na.grid(row=9,column=3)
        tsd_e = Entry(Frame,width=10,borderwidth=2)
        tsd_e.insert(END, 9e-3)
        tsd_e.grid(row=9,column=4)
        setattr(tempsd_threshold,'entry',tsd_e)
        tsd_o = Label(Frame, text = '', width=8, relief=SUNKEN)
        tsd_o.grid(row=9,column=5)
        setattr(tempsd_threshold,'olabel',tsd_o)

        nopts_stable = LSvari()
        setattr(nopts_stable,'name', 'nopts_stable')
        nps_na = Label(Frame, text = 'No. pts.\nfor check')
        nps_na.grid(row=10,column=3)
        nps_e = Entry(Frame,width=10,borderwidth=2)
        nps_e.insert(END, 30)
        nps_e.grid(row=10,column=4)
        setattr(nopts_stable,'entry',nps_e)
        nps_o = Label(Frame, text = '', width=8, relief=SUNKEN)
        nps_o.grid(row=10,column=5)
        setattr(nopts_stable,'olabel',nps_o)


def LS_update():
    global xData, yData, start_time

    def updateOptionMenu(optionmenu, optionmenu_variable, options):
        menu = optionmenu["menu"]
        menu.delete(0, 'end')
        for opt in options:
            menu.add_command(label=opt,command=lambda: optionmenu_variable.set(opt))
        

    for var in LSvars:
        if hasattr(var, 'entry'):
            val_cp = var.value			
            var.value = var.entry.get()
            if var.name == 'inputcurve':
                var.value = re.search(r'[0-9]+', var.value).group(0) #extract the number from the first index
            if val_cp != var.value:
                if var.name == 'channel':
                    LS.channel = channel.value
                    channel.olabel.config(text = LS.channel)
                    if LSdevice_modelNo == '340':
                        updateOptionMenu(inputcurve.optionmenu, inputcurve.entry, LS.incrvMenu)
                        inputcurve.value = LS.inputcurve
                        inputcurve.entry.set(inputcurve.value)
                        inputcurve.olabel.config(text = LS.inputcurve)
                    if LSdevice_modelNo == '336':
                        pass
                elif var.name == 'inputcurve':
                    LS.inputcurve = inputcurve.value
                    inputcurve.entry.set(inputcurve.value)
                    inputcurve.olabel.config(text = LS.inputcurve)
                elif var.name == 'hrange':
                    LS.hrange = hrange.value
                    hrange.olabel.config(text = LS.hrange)
                elif var.name == 'rampmode':
                    LS.rampmode = rampmode.value
                    rampmode.olabel.config(text = LS.rampmode)
                    LS.ramprate = ramprate.value
                    ramprate.olabel.config(text = LS.ramprate)
                elif var.name == 'ramprate':
                    LS.ramprate = ramprate.value
                    ramprate.olabel.config(text = LS.ramprate)
                elif var.name == 'setpt':
                    LS.setpoint = setpt.value
                elif var.name == 'prop':
                    LS.P = prop.value
                    prop.olabel.config(text = LS.P)
                elif var.name == 'inte':
                    LS.I = inte.value
                    inte.olabel.config(text = LS.I)
                elif var.name == 'deri':
                    LS.D = deri.value
                    deri.olabel.config(text = LS.D)
        
        
    setpt.olabel.config(text = LS.setpoint)
    nowtemp.value = LS.nowtemp
    LS_Curve._yData = np.append(LS_Curve._yData, nowtemp.value)
    nowtemp.olabel.config(text = nowtemp.value)
    elapsed_time = time.time() - start_time
    LS_Curve._xData = np.append(LS_Curve._xData, elapsed_time)
    houtput.olabel.config(text = LS.houtput)
	
def LS_continuous_monitor():
	ct = threading.currentThread()
	while True:
		LS_update()
		time.sleep(1)
		
def LS_continuous_renewplot(Curve_object):
	ct = threading.currentThread()
	while True:
		time.sleep(1)
		PlotMethods.FlushPlot(Curve_object)

def LS_stable_check(target_temp):
	global temp_stable_pass
	nopts_stable.olabel.config(text = nopts_stable.entry.get())
	if len(LS_Curve._yData) >= int(nopts_stable.entry.get()):
		segment_T = LS_Curve._yData[-int(nopts_stable.entry.get()):]
		mean_T = np.mean(segment_T)
		deltaT = np.round(np.absolute(float(target_temp) - mean_T),3)
		dtemp_threshold.olabel.config(text = deltaT)
		std_T = np.round(np.std(segment_T),3)
		tempsd_threshold.olabel.config(text = std_T)
		if deltaT < float(dtemp_threshold.entry.get()) and std_T < float(tempsd_threshold.entry.get()):
			temp_stable_pass = True
		else:
			temp_stable_pass = False
	else:
		temp_stable_pass = False
		
	return temp_stable_pass
		
def NC_InfoInit(Frame):
    global NCinfo,sample
    NCinfo = []

    sample = NCvari()
    NCinfo.append(sample)

    samp_na = Label(Frame, text = 'Sample name')
    samp_na.grid(row=0,column=0)
    samp_e = Entry(Frame,width=20,borderwidth=2)
    samp_e.insert(END, 'BerH-S2')
    samp_e.grid(row=1,column=0)
    setattr(sample,'name_entry',samp_e)

    len_na = Label(Frame, text = 'Separation (micron)')
    len_na.grid(row=0,column=1)
    len_e = Entry(Frame,width=10,borderwidth=2)
    len_e.insert(END, '60')
    len_e.grid(row=1,column=1)
    setattr(sample,'length_entry',len_e)

    wid_na = Label(Frame, text = 'Width (micron)')
    wid_na.grid(row=0,column=2)
    wid_e = Entry(Frame,width=10,borderwidth=2)
    wid_e.insert(END, '100')
    wid_e.grid(row=1,column=2)
    setattr(sample,'width_entry',wid_e)

    thic_na = Label(Frame, text = 'Thickness (micron)')
    thic_na.grid(row=0,column=3)
    thic_e = Entry(Frame,width=10,borderwidth=2)
    thic_e.insert(END, '80')
    thic_e.grid(row=1,column=3)
    setattr(sample,'thickness_entry',thic_e)

    cm_na = Label(Frame, text = 'Comment?')
    cm_na.grid(row=0,column=5)
    cm_e = Entry(Frame,width=20,borderwidth=2)
    cm_e.insert(END, '')
    cm_e.grid(row=1,column=5,rowspan=1)
    setattr(sample,'cm_entry',cm_e)
    
    def selectdir():
        #global directory
        filedirectory = filedialog.askdirectory()
        fd_e.delete(0, 'end')
        fd_e.insert(END, filedirectory)
    
    fd_na = Label(Frame, text = 'File directory:')
    fd_na.grid(row=3,column=0)
    fd_e = Entry(Frame,width=100,borderwidth=2)
    fd_e.insert(END, current_path)
    fd_e.grid(row=4,column=0,columnspan=10)
    setattr(sample,'fd_entry',fd_e)
    fd_bn = Button(Frame, text = "Select", command=selectdir)
    fd_bn.grid(row=3,column=1)
			
def NC_MeaEntriesInit(Frame):
    global NCvars,start_freq,end_freq,no_pts,logarithmic_mode,ACvolt,DCbias,DCvolt,wiremode,para_to_show
    NCvars = []

    start_freq = NCvari()
    setattr(start_freq,'name','Start Frequency (Hz)\n[min: 3uHz]')
    sf_na = Label(Frame, text = start_freq.name)
    sf_na.grid(row=0,column=0)
    sf_e = Entry(Frame,width=10,borderwidth=2)
    #sf_e.insert(END, '1e1')
    sf_e.insert(END, '1e0')
    sf_e.grid(row=0,column=1)
    setattr(start_freq,'entry',sf_e)
    NCvars.append(start_freq)

    end_freq = NCvari()
    setattr(end_freq,'name','End Frequency (Hz)\n[max: 35 MHz]')
    ef_na = Label(Frame, text = end_freq.name)
    ef_na.grid(row=1,column=0)
    ef_e = Entry(Frame,width=10,borderwidth=2)
    ef_e.insert(END, '1e6')
    #ef_e.insert(END, '1e7')
    ef_e.grid(row=1,column=1)
    setattr(end_freq,'entry',ef_e)
    NCvars.append(end_freq)

    no_pts = NCvari()
    setattr(no_pts,'name','No. of\npoints')
    np_na = Label(Frame, text = no_pts.name)
    np_na.grid(row=2,column=0)
    np_e = Entry(Frame,width=10,borderwidth=2)
    #np_e.insert(END, '6')
    np_e.insert(END, '7')
    np_e.grid(row=2,column=1)
    setattr(no_pts,'entry',np_e)
    NCvars.append(no_pts)

    logarithmic_mode = NCvari()
    setattr(logarithmic_mode,'name','Points\nspacing')
    lm_na = Label(Frame, text = logarithmic_mode.name)
    lm_na.grid(row=3,column=0)
    lm_e = StringVar()
    lm_e.set('Logarithmic')
    lm_eh = OptionMenu(Frame,lm_e,'Logarithmic','Linear')
    lm_eh.grid(row=3,column=1)
    setattr(logarithmic_mode,'entry',lm_e)
    NCvars.append(logarithmic_mode)

    ACvolt = NCvari()
    setattr(ACvolt,'name','AC amplitude (V)\n[0V-3V for <= 10MHz]')
    ac_na = Label(Frame, text = ACvolt.name)
    ac_na.grid(row=0,column=2)
    ac_e = Entry(Frame,width=10,borderwidth=2)
    #ac_e.insert(END, '0.5')
    ac_e.insert(END, '1')
    ac_e.grid(row=0,column=3)
    setattr(ACvolt,'entry',ac_e)
    NCvars.append(ACvolt)

    DCbias = NCvari()
    setattr(DCbias,'name','DC bias?')
    db_na = Label(Frame, text = DCbias.name)
    db_na.grid(row=1,column=2)
    db_e = StringVar()
    db_e.set('0')
    db_eh = Checkbutton(Frame,variable=db_e,onvalue='1',offvalue='0')
    db_eh.grid(row=1,column=3)
    setattr(DCbias,'entry',db_e)
    NCvars.append(DCbias)

    DCvolt = NCvari()
    setattr(DCvolt,'name','DC bias (V)\n[-40V - +40V]')
    dv_na = Label(Frame, text = DCvolt.name)
    dv_na.grid(row=2,column=2)
    dv_e = Entry(Frame,width=10,borderwidth=2)
    dv_e.insert(END, '0')
    dv_e.grid(row=2,column=3)
    setattr(DCvolt,'entry',dv_e)
    NCvars.append(DCvolt)

    wiremode = NCvari()
    setattr(wiremode,'name','Wiremode\n[2/3/4]')
    wm_na = Label(Frame, text = wiremode.name)
    wm_na.grid(row=3,column=2)
    setattr(wiremode,'value',NC.frontstate)
    #wm_e = IntVar()
    #wm_e.set(wiremode.value)
    wm_e = StringVar()
    wm_e.set(wiremode.value)
    wm_eh = OptionMenu(Frame,wm_e,'2','3','4')
    wm_eh.grid(row=3,column=3)
    setattr(wiremode,'entry',wm_e)
    NCvars.append(wiremode)

    para_to_show = NCvari()
    setattr(para_to_show,'name','Parameters to show')
    pts_na = Label(Frame, text = para_to_show.name)
    pts_na.grid(row=0,column=4)
    pts_e = StringVar()
    pts_e.set('GB')
    pts_eh = OptionMenu(Frame,pts_e,'GB','RX')
    pts_eh.grid(row=0,column=5)
    setattr(para_to_show,'entry',pts_e)
    NCvars.append(para_to_show)
			
def NC_CompenEntriesInit(Frame):
    global CP
    CP = Vari()
    #CP.append(sample)

    openmode_na = Label(Frame, text = 'Open compen')
    openmode_na.grid(row=0,column=0)
    openmode_e = StringVar()
    openmode_e.set('DAC')
    openmode_eh = OptionMenu(Frame,openmode_e,'None','Ambient','MAGNO','DAC','DAC+MAGNO')
    openmode_eh.grid(row=1,column=0)
    setattr(CP,'open_entry',openmode_e)

    shortmode_na = Label(Frame, text = 'Short compen')
    shortmode_na.grid(row=0,column=1)
    shortmode_e = StringVar()
    shortmode_e.set('None')
    shortmode_eh = OptionMenu(Frame,shortmode_e,'None','Ambient','DAC')
    shortmode_eh.grid(row=1,column=1)
    setattr(CP,'short_entry',shortmode_e)
	

def Data_compensation(R_raw, X_raw):

    def find_closest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return [array[idx],idx]


    compen_dir = r'\\S4\Datenpool\Yuk Tai\Data and Analysis\Compensation'
    t = nowtemp.value
    f = NC.ACfreq
        
    if CP.open_entry.get() == 'None':
        G_o = 0
        B_o = 0
    elif CP.open_entry.get() == 'DAC':
        opendirname = os.path.join(compen_dir,'DAC_Opencompensation 20210426')
        openfilepath = os.path.join(opendirname,'2021-04-26_DAC_opencompen_1.0V_295K.txt')	#only 1 file now
        header = np.genfromtxt(openfilepath,delimiter='\t',dtype=str)[0]
        header = np.char.strip(header)
        Freqcol_ind = np.where(header=='Freq')[0][0]
        Gcol_ind = np.where(header=='G_raw')[0][0]
        Bcol_ind = np.where(header=='B_raw')[0][0]
        content = np.genfromtxt(openfilepath,delimiter='\t',dtype=float)[3:]  #[1:]: skip header,unit,comment
        Freq_open = np.hsplit(content,len(header))[Freqcol_ind]          
        G_open = np.hsplit(content,len(header))[Gcol_ind]
        B_open = np.hsplit(content,len(header))[Bcol_ind]
        clos_freq_idx = find_closest(Freq_open,f)[1]
        G_o = G_open[clos_freq_idx]
        B_o = B_open[clos_freq_idx]
        
    elif CP.open_entry.get() == 'DAC+MAGNO':
        #opendirname = os.path.join(compen_dir,'DAC+MAGNO_Opencompensation 20210415')
        #compen_tlist = [294,290,280,260,240,220,200,180,160,140,120,100,80,60,50,40,30,25]
        #compentemp = find_closest(compen_tlist,t)[0];
        #compenfilename = 'DAC+MAGNO_' + str(compentemp) + 'K.txt'
        #openfilepath = os.path.join(opendirname,compenfilename)
        opendirname = os.path.join(compen_dir,'DAC+MAGNO_Opencompensation 20210527')
        compen_tlist = np.arange(2,31)*10
        compen_tlist = np.insert(compen_tlist,0,12)
        compen_tlist = np.insert(compen_tlist,-1,295)
        compentemp = find_closest(compen_tlist,t)[0];
        openfilename = str(compentemp) + 'K.txt'
        openfilepath = os.path.join(opendirname,openfilename)
        
        header = np.genfromtxt(openfilepath,delimiter='\t',dtype=str)[0]
        header = np.char.strip(header)
        Freqcol_ind = np.where(header=='Freq')[0][0]
        Gcol_ind = np.where(header=='G_raw')[0][0]
        Bcol_ind = np.where(header=='B_raw')[0][0]
        content = np.genfromtxt(openfilepath,delimiter='\t',skip_header=3)
        content = np.transpose(content)
        Freq_open = content[Freqcol_ind]          
        G_open =content[Gcol_ind]
        B_open = content[Bcol_ind]
        clos_freq_idx = find_closest(Freq_open,f)[1]
        G_o = G_open[clos_freq_idx]
        B_o = B_open[clos_freq_idx]
        
    elif CP.open_entry.get() == 'MAGNO':
        opendirname = os.path.join(compen_dir,'MAGNO_Opencompensation 20210506')
        compen_tlist = [295,280,260,240,220,200,180,160,140,100,60,40,20,15]
        compentemp = find_closest(compen_tlist,t)[0];
        compenfilename = 'MAGNO_opencompen_1.0V_' + str(compentemp) + 'K.txt'
        openfilepath = os.path.join(opendirname,compenfilename)
        
        header = np.genfromtxt(openfilepath,delimiter='\t',dtype=str)[0]
        header = np.char.strip(header)
        Freqcol_ind = np.where(header=='Freq')[0][0]
        Gcol_ind = np.where(header=='G_raw')[0][0]
        Bcol_ind = np.where(header=='B_raw')[0][0]
        content = np.genfromtxt(openfilepath,delimiter='\t',skip_header=3)
        content = np.transpose(content)
        Freq_open = content[Freqcol_ind]
        G_open = content[Gcol_ind]
        B_open = content[Bcol_ind]
        clos_freq_idx = find_closest(Freq_open,f)[1]
        G_o = G_open[clos_freq_idx]
        B_o = B_open[clos_freq_idx]
        
        
        

    elif CP.open_entry.get() == 'Ambient' or 'Novo':
        #print("OP is in")
        if CP.open_entry.get() == 'Ambient':
            opendirname = os.path.join(compen_dir,'Amb_Opencompensation')  
            AmbO_tlist = np.arange(118,dtype=int)*(2.5)+7.5
            closest_temp,idx = find_closest(AmbO_tlist,t)
            
        elif CP.open_entry.get() == 'Novo':
            opendirname = os.path.join(compen_dir,'Novo_4K_Opencompensation')
            NovoO_tlist = np.arange((300/5),dtype=int)*(5)+5
            closest_temp,idx = find_closest(NovoO_tlist,t)
            
        closest_temp_str = str(closest_temp) + ' K.txt'
        openfilepath = os.path.join(opendirname,closest_temp_str)
        content = np.genfromtxt(openfilepath,delimiter='\t',dtype=float)[1:]  #[1:]: skip header
        Freq_open = np.hsplit(content,6)[0]          #content has a sixth column filled with 'nan'
        G_open = np.hsplit(content,6)[2]
        B_open = np.hsplit(content,6)[3]            
        clos_freq_idx = find_closest(Freq_open,f)[1]
        G_o = G_open[clos_freq_idx]
        B_o = B_open[clos_freq_idx]

    ############Short compensation##########
    if CP.short_entry.get() == 'None':
        R_s = 0
        X_s = 0
    elif CP.short_entry.get() == 'DAC':
        shortdirname = os.path.join(compen_dir,'DAC_Shortcompensation 20210427')
        shortfilepath = os.path.join(shortdirname,'2021-04-27_DAC_shortcompen_1.0V_295K.txt')	#only 1 file now
        header = np.genfromtxt(shortfilepath,delimiter='\t',dtype=str)[0]
        header = np.char.strip(header)
        Freqcol_ind = np.where(header=='Freq')[0][0]
        Gcol_ind = np.where(header=='G')[0][0]
        Bcol_ind = np.where(header=='B')[0][0]
        content = np.genfromtxt(shortfilepath,delimiter='\t',dtype=float)[3:]  #[1:]: skip header,unit,comment
        Freq_short = np.hsplit(content,len(header))[Freqcol_ind]          
        G_short = np.hsplit(content,len(header))[Gcol_ind]
        B_short = np.hsplit(content,len(header))[Bcol_ind]
        clos_freq_idx = find_closest(Freq_short,f)[1]
        G_s = G_short[clos_freq_idx]
        B_s = B_short[clos_freq_idx]
        
        R_s = G_s/((G_s**2) + (B_s**2))
        X_s = -B_s/((G_s**2) + (B_s**2))
    elif CP.short_entry.get() == 'Ambient':
        shortdirname = os.path.join(compen_dir,'Amb_Shortcompensation')  
        AmbS_tlist = np.arange(118,dtype=int)*(2.5)+7.5
        closest_temp,idx = find_closest(AmbS_tlist,t)
            
        closest_temp_str = str(closest_temp) + ' K.txt'
        shortfilepath = os.path.join(shortdirname,closest_temp_str)
        content = np.genfromtxt(shortfilepath,delimiter='\t',dtype=float)[1:]  #[1:]: skip header
        Freq_short = np.hsplit(content,6)[0]          #content has a sixth column filled with 'nan'
        G_short = np.hsplit(content,6)[2]
        B_short = np.hsplit(content,6)[3]
        clos_freq_idx = find_closest(Freq_short,f)[1]
        
        G_s = G_short[clos_freq_idx]
        B_s = B_short[clos_freq_idx]
        
        R_s = G_s/((G_s**2) + (B_s**2))
        X_s = -B_s/((G_s**2) + (B_s**2))



    nominator = (1-G_o*(R_raw-R_s)+B_o*(X_raw-X_s))**2+(G_o*(X_raw-X_s)+B_o*(R_raw-R_s))**2
    R = ((R_raw-R_s)*(1-G_o*(R_raw-R_s)+B_o*(X_raw-X_s))-(X_raw-X_s)*(G_o*(X_raw-X_s)+B_o*(R_raw-R_s)))/nominator;
    X = ((X_raw-X_s)*(1-G_o*(R_raw-R_s)+B_o*(X_raw-X_s))+(R_raw-R_s)*(G_o*(X_raw-X_s)+B_o*(R_raw-R_s)))/nominator

    return [R,X]




def NC_freqptslist_cal():
	sf = float(start_freq.entry.get())
	ef = float(end_freq.entry.get())
	nopt = int(no_pts.entry.get())
	scal = logarithmic_mode.entry.get()
	
	NC_Curve_a._ax.set_xlabel('Freq (Hz)')
	NC_Curve_b._ax.set_xlabel('Freq (Hz)')
	if scal == 'Logarithmic':
		NC_Curve_a._ax.set_xscale('log')
		NC_Curve_b._ax.set_xscale('log')
		#incre = (np.log10(ef) - np.log10(sf))/(nopt-1)
		#pt_array = 10**np.arange(np.log10(sf),np.log10(ef)+incre,incre)
		pt_array = 10**np.linspace(np.log10(sf),np.log10(ef),nopt)
	elif scal == 'Linear':
		NC_Curve_a._ax.set_xscale('linear')
		NC_Curve_b._ax.set_xscale('linear')
		#incre = (ef - sf)/(nopt-1)
		#pt_array = np.arange(sf, ef+incre, incre)
		pt_array = np.linspace(sf, ef, nopt)
	
	pt_array = np.flip(pt_array)
	return pt_array
	
def NC_measure():
    global arrFreq,arrTemp,arrG,arrB,arrR,arrX,arrC,arrepsr1,arrepsr2,arrcond,arrrho,arrGraw,arrBraw

    ## CANNOT use NC_Curve_a._ax.cla(), which will erase the curve itself instead of the elements
    NC_Curve_a.clear()
    NC_Curve_b.clear()

    NC.DCbias = DCbias.entry.get()
    if NC.DCbias == '1':
        NC.DCvolt = float(DCvolt.entry.get())
    NC.ACvolt = float(ACvolt.entry.get())

    pt_array = NC_freqptslist_cal()
    #print(pt_array)

    plt_para = para_to_show.entry.get()
    if plt_para == 'GB':
        NC_Curve_a._ax.set_ylabel('G')
        NC_Curve_b._ax.set_ylabel('B')
        NC_Curve_b._ax.set_yscale('log')
    elif plt_para == 'RX':
        NC_Curve_a._ax.set_ylabel('R')
        NC_Curve_b._ax.set_ylabel('X')

    if wiremode.entry.get() != NC.frontstate:
        NC.frontstate = wiremode.entry.get()
        NC.print_message("Front state changed to %s-wire mode." %NC.frontstate)


    for pt in pt_array:
        NC.ACfreq = pt
        NC.print_message("Measurement started. AC freq = %f Hz." %NC.ACfreq)
        NC.measurement_trigger()
        NC.check_task_state(interval=1/pt)
        [realZ_raw, imgZ_raw, freq, status, ref_mea_status] = NC.return_Z()
        realZ_raw = float(realZ_raw)
        imgZ_raw = float(imgZ_raw)
        [realZ,imgZ] = Data_compensation(realZ_raw,imgZ_raw)
        #print(realZ,imgZ)
        
        freq = float(freq)
        denominator = realZ**2 + imgZ**2
        G = realZ/denominator
        B = -imgZ/denominator
        
        denominator_raw = realZ_raw**2 + imgZ_raw**2
        Graw = realZ_raw/denominator_raw
        Braw = -imgZ_raw/denominator_raw

        NC_Curve_a._xData = np.append(NC_Curve_a._xData, freq)
        NC_Curve_b._xData = np.append(NC_Curve_b._xData, freq)
        if plt_para == 'GB':
            NC_Curve_a._yData = np.append(NC_Curve_a._yData, G)
            NC_Curve_b._yData = np.append(NC_Curve_b._yData, B)
        elif plt_para == 'RX':
            NC_Curve_a._yData = np.append(NC_Curve_a._yData, realZ)
            NC_Curve_b._yData = np.append(NC_Curve_b._yData, imgZ)
        PlotMethods.FlushPlot(NC_Curve_a)
        PlotMethods.FlushPlot(NC_Curve_b)
        
        sample_length = float(sample.length_entry.get())
        sample_area = float(sample.width_entry.get())*float(sample.thickness_entry.get())
        geometric_factor = (sample_length/sample_area)*1e6
        
        
        arrFreq = np.append(arrFreq,freq)
        arrTemp = np.append(arrTemp,nowtemp.value)
        arrG = np.append(arrG,G)
        arrB = np.append(arrB,B)
        arrR = np.append(arrR,realZ)
        arrX = np.append(arrX,imgZ)
        arrC = np.append(arrC,B/freq)
        arrepsr1 = np.append(arrepsr1,geometric_factor*B/(scipy.constants.epsilon_0*2*scipy.constants.pi*freq))
        arrepsr2 = np.append(arrepsr2,geometric_factor*G/(scipy.constants.epsilon_0*2*scipy.constants.pi*freq))
        arrcond = np.append(arrcond,G*geometric_factor/100)
        arrrho = np.append(arrrho,G/(G**2+B**2)/geometric_factor/100)
        arrGraw = np.append(arrGraw,Graw)
        arrBraw = np.append(arrBraw,Braw)
        
    NC.print_message("Measurement completed.")

def NC_single_measure():
	DataArray_initialise()
	NC_Curve_c._ax.cla()
	NC_Curve_d._ax.cla()
	NC_Curve_c._ax.set_xscale('log')
	NC_Curve_d._ax.set_xscale('log')
	NC_Curve_d._ax.set_yscale('log')
	NC_Curve_c._ax.set_xlabel('Freq (Hz)')
	NC_Curve_d._ax.set_xlabel('Freq (Hz)')
	NC_Curve_c._ax.set_ylabel('epsr1')
	NC_Curve_d._ax.set_ylabel('epsr2')
	
	NC.print_message("Single measurement started")
	NC_measure()
	
	curve_r1 = Curve(NC_Canvas2,0)
	curve_r2 = Curve(NC_Canvas2,1)
	curve_r1._xData = arrFreq
	curve_r2._xData = arrFreq
	curve_r1._yData = arrepsr1
	curve_r2._yData = arrepsr2	
	PlotMethods.FlushPlot(curve_r1)
	PlotMethods.FlushPlot(curve_r2)
	
	NC.print_message("Single measurement finished")

def datastack(*args):
	arr1 = np.empty_like(args[0])
	for arg in args:
		arr1 = np.vstack((arr1,arg))
	arr2 = np.delete(arr1,0,0)
	arr3 = np.transpose(arr2)
	return arr3
	
def NC_savedata(**kwargs):
    global arrFreq,arrTemp,arrG,arrB,arrR,arrX,arrC,arrepsr1,arrepsr2,arrcond,arrrho,arrGraw,arrBraw

    mea_type = kwargs.get('mea_type','single')
        
    timeObj = time.localtime(time.time())
    timeanddate = '%04d-%02d-%02d' %(timeObj.tm_year, timeObj.tm_mon, timeObj.tm_mday)

    header_str = ['Freq','Temp','epsr1','epsr2','cond','rho','G','B','C','R','X','G_raw','B_raw']
    header_row = np.expand_dims(header_str,axis=0)
    unit_str = ['Hz','K','','','ohm-1 cm-1','ohm cm-1','S','S','F','ohm','ohm','S','S']
    unit_row = np.expand_dims(unit_str,axis=0)
    cm_str = [sample.cm_entry.get() for i in range(len(header_str))]
    cm_row = np.expand_dims(cm_str,axis=0)


    fname = timeanddate+'_'+sample.name_entry.get()
    
    if sample.cm_entry.get() is not '':
        fname = fname + '_' + sample.cm_entry.get()

    if NC.DCbias == '1': 
        fname =  fname + '_' +str(NC.ACvolt)+'Vac_'+str(NC.DCvolt)+'Vdc'
    else:
        fname =  fname + '_' +str(NC.ACvolt)+'V'
    
    all_data = datastack(arrFreq,arrTemp,arrepsr1,arrepsr2,arrcond,arrrho,arrG,arrB,arrC,arrR,arrX,arrGraw,arrBraw)

    if mea_type == 'continuous':
        freq_union = np.union1d(all_data[:,0],all_data[:,0])	#find the union = remove repeated units
        header_row[:,[1,0]] = header_row[:,[0,1]]
        unit_row[:,[1,0]] = unit_row[:,[0,1]]
        fnameroot = fname
        for i in freq_union:
            if sample.cm_entry.get() == '':
                cm_str = ['%s Hz' %i for j in range(len(header_str))]
                cm_row = np.expand_dims(cm_str,axis=0)
            cm_row[:,[1,0]] = cm_row[:,[0,1]]
            ad = np.empty_like(all_data[0,:])
            for j in range(len(all_data[:,0])):
                if i == all_data[j,0]:
                    ad = np.vstack((ad,all_data[j,:]))
                    
            ad = np.delete(ad,0,0)
                
            ad[:,[1,0]] = ad[:,[0,1]]							#Swap 'Temp' to 1st colume with 'Freq'
            
            #fname = fnameroot+str(i)+'Hz'
            fname = fnameroot+str(i)+'Hz_'+'%sK-%sK' %(ad[:,0][0],ad[:,0][-1])
            fname_prefix = fname
            i = 1
            while os.path.exists(fname+'.txt'):
                fname = fname_prefix + '-%03d'%i
                i += 1
            #fpath = os.path.join(current_path,fname)
            fpath = os.path.join(sample.fd_entry.get(),fname)
            f = open(fpath+'.txt','w')
            #f = open(fname+'.txt','w')			#Sometimes, without specifying fullpath, file is located in where Python is installed, so permission might be denied
            np.savetxt(f, header_row, fmt='%5s' ,delimiter='\t',comments='')
            np.savetxt(f, unit_row, fmt='%5s' ,delimiter='\t',comments='')
            np.savetxt(f, cm_row, fmt='%5s' ,delimiter='\t',comments='')
            np.savetxt(f, ad, fmt='%5s' ,delimiter='\t',comments='')
            f.close()
            
    else:	
             
        if mea_type == 'single':
            fname = fname
        elif mea_type == 'stable':
            fname = fname+'_'+str(nowtemp.value)+'K'
            
        fname_prefix = fname
        i = 1
        #fpath = os.path.join(current_path,fname)
        fpath = os.path.join(sample.fd_entry.get(),fname)
        while os.path.exists(fpath+'.txt'):
            fname = fname_prefix + '-%03d'%i
            fpath = os.path.join(sample.fd_entry.get(),fname)
            i += 1
        f = open(fpath+'.txt','w')
        np.savetxt(f, header_row, fmt='%5s' ,delimiter='\t',comments='')
        np.savetxt(f, unit_row, fmt='%5s' ,delimiter='\t',comments='')
        if sample.cm_entry.get() == '':
            cm_str = ['%s K' %str(nowtemp.value) for j in range(len(header_str))]
            cm_row = np.expand_dims(cm_str,axis=0)
        np.savetxt(f, cm_row, fmt='%5s' ,delimiter='\t',comments='')
        np.savetxt(f, all_data, fmt='%5s' ,delimiter='\t',comments='')
        f.close()
        
    NC.print_message("Data saved. Filename: %s" %fname)
    
def NC_savedata_Continuous(**kwargs):
    global arrFreq,arrTemp,arrG,arrB,arrR,arrX,arrC,arrepsr1,arrepsr2,arrcond,arrrho,arrGraw,arrBraw

    meaStatus = kwargs.get('meaStatus','On-going')
        
    timeObj = time.localtime(time.time())
    timeanddate = '%04d-%02d-%02d' %(timeObj.tm_year, timeObj.tm_mon, timeObj.tm_mday)

    header_str = ['Temp','Freq','epsr1','epsr2','cond','rho','G','B','C','R','X','G_raw','B_raw']
    header_row = np.expand_dims(header_str,axis=0)
    unit_str = ['K','Hz','','','ohm-1 cm-1','ohm cm-1','S','S','F','ohm','ohm','S','S']
    unit_row = np.expand_dims(unit_str,axis=0)
    cm_str = [sample.cm_entry.get() for i in range(len(header_str))]
    cm_row = np.expand_dims(cm_str,axis=0)

    ACvolt = kwargs.get('ACvolt',1)
    DCbias = kwargs.get('DCbias','0')
    DCvolt = kwargs.get('DCvolt',0)
    
    fname = timeanddate+'_'+sample.name_entry.get()
    
    if sample.cm_entry.get() is not '':
        fname = fname + '_' + sample.cm_entry.get()
    if DCbias == '1': 
        fname =  fname + '_' +str(ACvolt)+'Vac_'+str(DCvolt)+'Vdc'
    else:
        fname =  fname + '_' +str(ACvolt)+'V'
    
    
    freq_union = np.union1d(arrFreq,arrFreq)	#find the union = remove repeated units
    fnameroot = fname
    
    
    
    if meaStatus == 'On-going':
        for i in freq_union:
            if sample.cm_entry.get() == '':
                cm_str = ['%s Hz' %i for j in range(len(header_str))]
                cm_row = np.expand_dims(cm_str,axis=0)
            cm_row[:,[1,0]] = cm_row[:,[0,1]]
            
            for j in range(1,len(freq_union)+1):
                if i == arrFreq[-j]:
                    newDataRow = [arrTemp[-j],arrFreq[-j],arrepsr1[-j],arrepsr2[-j],arrcond[-j],arrrho[-j],arrG[-j],arrB[-j],arrC[-j],arrR[-j],arrX[-j],arrGraw[-j],arrBraw[-j]]
                    newDataRow = np.expand_dims(newDataRow,axis=0)
                    
                    
            fname = fnameroot+'_'+str(i)+'Hz'+'.txt'
            fpath = os.path.join(sample.fd_entry.get(),fname)  
                    
            if not os.path.exists(fpath):
                f = open(fpath,'w')
                np.savetxt(f, header_row, fmt='%5s' ,delimiter='\t',comments='')
                np.savetxt(f, unit_row, fmt='%5s' ,delimiter='\t',comments='')
                np.savetxt(f, cm_row, fmt='%5s' ,delimiter='\t',comments='')
            else:
                f = open(fpath,'a')
            
            np.savetxt(f, newDataRow, fmt='%5s' ,delimiter='\t',comments='')
            f.close()
    elif meaStatus == 'End':
        for i in freq_union:         
            fname = fnameroot+'_'+str(i)+'Hz'+'.txt'
            fpath = os.path.join(sample.fd_entry.get(),fname)  
            content = np.genfromtxt(fpath,delimiter='\t',dtype=float)[3:]
            arrTemp = content[:,0]
            fnameWithTempRange = fnameroot+'_'+str(i)+'Hz_'+ '%sK-%sK' %(arrTemp[0],arrTemp[-1]) +'.txt'
            #fpathWithTempRange = os.path.join(current_path,fnameWithTempRange)
            fpathWithTempRange = os.path.join(sample.fd_entry.get(),fnameWithTempRange)
            os.rename(r'%s' %fpath, r'%s' %fpathWithTempRange)
	
def NC_stablised_measure():
	NC_Curve_c._ax.cla()
	NC_Curve_d._ax.cla()
	NC_Curve_c._ax.set_xlabel('Freq (Hz)')
	NC_Curve_d._ax.set_xlabel('Freq (Hz)')
	NC_Curve_c._ax.set_ylabel('epsr1')
	NC_Curve_d._ax.set_ylabel('epsr2')
	
	def caladd():
		global textbox,st_entry,et_entry,step_entry
		st_temp = float(st_entry.get())
		et_temp = float(et_entry.get())
		step = float(step_entry.get())
		tlist = np.linspace(st_temp, et_temp, num=round(abs(st_temp-et_temp)/step+1))
		#print(tlist)
		for t in tlist:
			textbox.insert(END, "%.3f\n" %t)
		textbox.see("end")

	def cleartext():
		global textbox
		textbox.delete('1.0', END)
	
	def proceed():
		global popup,textbox, temp_queue, holding_var
		text = textbox.get("1.0",END)
		temp_queue = text.split('\n')
		temp_queue = list(filter(None, temp_queue))
		popup.destroy()
		return temp_queue
		
	def cancel():
		global popup
		#holding_var.set(1)
		popup.destroy()
		
	def open_temppts_planner():
		global temp_queue,popup,textbox,st_entry,et_entry,step_entry
		temp_queue = []
		popup = Toplevel()
		#holding_var = IntVar()
		textbox=Text(popup, wrap=WORD, height=30, width=10)
		textbox.grid(row=0,column=0,rowspan=100)
		st_label = Label(popup, text = 'Start temp (K)')
		st_label.grid(row=0,column=1)
		st_entry = Entry(popup, width=10,borderwidth=2)
		st_entry.grid(row=1,column=1)
		et_label = Label(popup, text = 'End temp (K)')
		et_label.grid(row=2,column=1)
		et_entry = Entry(popup, width=10,borderwidth=2)
		et_entry.grid(row=3,column=1)
		step_label = Label(popup, text = 'Step (K)')
		step_label.grid(row=4,column=1)
		step_entry = Entry(popup, width=10,borderwidth=2)
		step_entry.grid(row=5,column=1)
		add_btn = Button(popup, text = 'Add', command = caladd)
		add_btn.grid(row=20,column=1)
		clr_btn = Button(popup, text = 'Clear', command = cleartext)
		clr_btn.grid(row=21,column=1)
		pcd_btn = Button(popup, text = 'Proceed', command = proceed)
		pcd_btn.grid(row=30,column=1)
		cel_btn = Button(popup, text = 'Cancel', command = cancel)
		cel_btn.grid(row=31,column=1)
		popup.wait_window()
		#wait_variable(holding_var)
		return temp_queue
	
	temp_queue = open_temppts_planner()
	
	if not temp_queue == []:
		NC.print_message("Stablization measurement started.")
		
		curves_r1 = []
		curves_r2 = []
		freq_low = []
		freq_high = []
		r1_low = []
		r1_high = []
		r2_low = []
		r2_high = []
		c = 0
		for t in temp_queue:
			LS.setpoint = t
			DataArray_initialise()
			time.sleep(1)
			while not LS_stable_check(t):
				NC.print_message("Target temp: " + t +". Stablization not passed.")
				time.sleep(1)
			NC.print_message("Stablization passed.")
			NC_measure()
			
			if logarithmic_mode.entry.get() == 'Logarithmic':
				NC_Curve_c._ax.set_xscale('log')
				NC_Curve_d._ax.set_xscale('log')
			elif logarithmic_mode.entry.get() == 'Linear':
				NC_Curve_c._ax.set_xscale('linear')
				NC_Curve_d._ax.set_xscale('linear')
				
			#print("c = ",c)
			curves_r1.append(Curve(NC_Canvas2,0))
			curves_r2.append(Curve(NC_Canvas2,1))
			curves_r1[c]._xData = arrFreq
			curves_r2[c]._xData = arrFreq
			freq_low.append(np.min(arrFreq))
			freq_high.append(np.max(arrFreq))
			curves_r1[c]._yData = arrepsr1
			r1_low.append(np.min(arrepsr1))
			r1_high.append(np.max(arrepsr1))
			curves_r2[c]._yData = arrepsr2
			r2_low.append(np.min(arrepsr2))
			r2_high.append(np.max(arrepsr2))
			x_min = np.min(freq_low)
			x_max = np.max(freq_high)
			r1_min = np.min(r1_low)
			r1_max = np.max(r1_high)
			r2_min = np.min(r2_low)
			r2_max = np.max(r2_high)	
			AddPlot(curves_r1[c],x_range=[x_min,x_max],y_range=[r1_min,r1_max])
			AddPlot(curves_r2[c],x_range=[x_min,x_max],y_range=[r2_min,r2_max])
			c += 1
			
			NC_savedata(mea_type = 'stable')
			#print("data saved")
		NC.print_message("Stablization measurement finished.")
	
def NC_continuous_measure():
    def estimate():
        global textbox,et_entry,rr_entry
        st_temp = float(nowtemp.value)
        et_temp = float(et_entry.get())
        rrate = float(rr_entry.get())
        duration = abs(et_temp - st_temp)/rrate
        textbox.insert(END, "Duration:" + "%.3f minutes\n" %duration)
        timeObj = time.localtime(time.time()+duration*60)
        textbox.insert(END, "Finish at %02d:%02d:%02d\n" %(timeObj.tm_hour, timeObj.tm_min, timeObj.tm_sec))
        textbox.see("end")
        

    def cleartext():
        global textbox
        textbox.delete('1.0', END)

    def proceed():
        global popup,et_entry,rr_entry

        proceeding = True
        rrate = rr_entry.get()
        ramprate.entry.delete(0, 'end')
        ramprate.entry.insert(END,rrate)
        et_temp = et_entry.get()
        setpt.entry.delete(0, 'end')
        setpt.entry.insert(END,et_temp)
        popup.destroy()
        
        DataArray_initialise()
        NC.print_message("Continuous measurement started.")
        NC_Curve_c._ax.cla()
        NC_Curve_d._ax.cla()
        NC_Curve_c._ax.set_xlabel('Temp (K)')
        NC_Curve_d._ax.set_xlabel('Temp (K)')
        NC_Curve_c._ax.set_ylabel('epsr1')
        NC_Curve_d._ax.set_ylabel('epsr2')
        
        temp_low = []
        temp_high = []
        r1_low = []
        r1_high = []
        r2_low = []
        r2_high = []
        curves_r1 = []
        curves_r2 = []
        
        pt_array = NC_freqptslist_cal()
        ACvolt = NC.ACvolt
        DCbias = NC.DCbias
        DCvolt = NC.DCvolt
                
        while not LS_stable_check(et_temp):
            #time.sleep(1)
            NC_measure()
            
            fresh_arrFreq = arrFreq[-len(pt_array):]
            fresh_arrTemp = arrTemp[-len(pt_array):]
            fresh_arrepsr1 = arrepsr1[-len(pt_array):]
            fresh_arrepsr2 = arrepsr2[-len(pt_array):]
            for i in range(len(fresh_arrFreq)):
                if any(curves_r1[c]._freq == fresh_arrFreq[i] for c in range(len(curves_r1))):
                    c = [k for k, j in enumerate(curves_r1) if j._freq == fresh_arrFreq[i]][0]
                    curves_r1[c]._xData = np.append(curves_r1[c]._xData, fresh_arrTemp[i])
                    curves_r1[c]._yData = np.append(curves_r1[c]._yData, fresh_arrepsr1[i])
                    curves_r2[c]._xData = np.append(curves_r2[c]._xData, fresh_arrTemp[i])
                    curves_r2[c]._yData = np.append(curves_r2[c]._yData, fresh_arrepsr2[i])
                else:
                    c1 = Curve(NC_Canvas2,0)
                    setattr(c1,'_freq',fresh_arrFreq[i])
                    c1._xData = np.append(c1._xData, fresh_arrTemp[i])
                    c1._yData = np.append(c1._yData, fresh_arrepsr1[i])
                    curves_r1.append(c1)
                    c2 = Curve(NC_Canvas2,1)
                    setattr(c2,'_freq',fresh_arrFreq[i])	
                    c2._xData = np.append(c2._xData, fresh_arrTemp[i])
                    c2._yData = np.append(c2._yData, fresh_arrepsr2[i])
                    curves_r2.append(c2)
            et_temp = setpt.entry.get()
            threading.Thread(target=FlushMultiPlots, args=(curves_r1,)).start()
            threading.Thread(target=FlushMultiPlots, args=(curves_r2,)).start()
            threading.Thread(target=NC_savedata_Continuous, kwargs={'ACvolt':ACvolt, 'DCbias':DCbias, 'DCvolt':DCvolt}).start()
        time.sleep(1)       # The savedata thread in the last loop might not finish yet
        NC_savedata_Continuous(meaStatus='End', ACvolt=ACvolt, DCbias=DCbias, DCvolt=DCvolt)
        NC.print_message("Continuous measurement finished.")
		
    def cancel():
        popup.destroy()
		
    def open_estimater():
        global popup,textbox,et_entry,rr_entry
        popup = Toplevel()
        #holding_var = IntVar()
        textbox=Text(popup, wrap=WORD, height=10, width=30)
        textbox.grid(row=10,column=0,columnspan=10)
        et_label = Label(popup, text = 'End temp (K)')
        et_label.grid(row=0,column=0)
        et_entry = Entry(popup, width=10,borderwidth=2)
        et_entry.grid(row=0,column=1)
        rr_label = Label(popup, text = 'Ramp rate (K/min)')
        rr_label.grid(row=0,column=2)
        rr_entry = Entry(popup, width=10,borderwidth=2)
        rr_entry.grid(row=0,column=3)
        
        add_btn = Button(popup, text = 'Estimate', command = estimate)
        add_btn.grid(row=0,column=7)
        pcd_btn = Button(popup, text = 'Proceed', command = lambda: threading.Thread(target=proceed, args=()).start())
        pcd_btn.grid(row=0,column=8)
        cel_btn = Button(popup, text = 'Cancel', command = cancel)
        cel_btn.grid(row=0,column=9)
        popup.wait_window()

    open_estimater()
	
def NC_time_polarization_measure():
	NC.print_message("Time polarization measurement is triggered")

def say_hello():
	NCtextbox.insert(END,"Hello \n")
	NCtextbox.see("end")

def	NC_ActionsInit(Frame):
	start_button = Button(Frame,text = "START", command =lambda: threading.Thread(target=NC_single_measure, args=()).start())
	start_button.grid(row=6,column=0)
	
	datafile_button = Button(Frame,text = "Save data", command = lambda: threading.Thread(target=NC_savedata, args=()).start())
	datafile_button.grid(row=7,column=0)
	
	mea_stable_button = Button(Frame,text = "Stablized\nsequence\nmeasurments", command = lambda: threading.Thread(target=NC_stablised_measure, args=()).start())
	mea_stable_button.grid(row=6,column=2, rowspan=2)
	
	mea_contin_button = Button(Frame,text = "Continuous\nmeasurments", command = lambda: threading.Thread(target=NC_continuous_measure, args=()).start())
	mea_contin_button.grid(row=6,column=3, rowspan=2)
	
	mea_timepol_button = Button(Frame,text = "Time polarization\nmeasurments", command = lambda: threading.Thread(target=NC_time_polarization_measure, args=()).start())
	mea_timepol_button.grid(row=8,column=3, rowspan=2)
	
	all_cali_button = Button(Frame,text = "ALL calibration", command =lambda: threading.Thread(target=NC.all_calibration_trigger, args=()).start())
	all_cali_button.grid(row=6,column=7)
	
	loadshort_cali_button = Button(Frame,text = "Load-short calibration", command =lambda: threading.Thread(target=NC.loadshort_calibration_trigger, args=()).start())
	loadshort_cali_button.grid(row=7,column=7)
	
	abort_button = Button(Frame,text = "Abort running task", command =lambda: threading.Thread(target=NC.measurement_abort, args=()).start())
	abort_button.grid(row=6,column=9)
		
	
	hello_button = Button(Frame,text = "Say Hello", command =lambda: threading.Thread(target=say_hello, args=()).start())
	hello_button.grid(row=7,column=9)
	
	Button(Frame, text="Quit", command=quit).grid(row=100,column=100)
	
	
		

if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    root = Tk()
    root.geometry("1760x990")
    #root.geometry("1600x900")
    root.title('Novocontrol Controlor')
    plt.ion()						# enable automatic update plots from plt 


    ### Initialise device(s) communication
    rm = ResourceManage.rm_initiate()
    idn_dict = ResourceManage.rm_dict()
    for d in [d for d in idn_dict if "LSCI,MODEL" in d]:
        result = re.search('LSCI,MODEL(.*),(.*),(.*)', d)
        LSdevice_modelNo = result.group(1)	
    # Initialise Lakeshore = temperature controller
    if LSdevice_modelNo == '340':
        LS = LakeShore340Init.LSall(rm,idn_dict)
    elif LSdevice_modelNo == '336':
        LS = LakeShore336Init.LSall(rm,idn_dict)


    #### Initialise frames for the UI
    LSFrame = LabelFrame(root,text="Lakeshore"+LSdevice_modelNo)
    LSFrame.grid(row=0,column=0)
    LSparaFrame = LabelFrame(LSFrame,text="Parameters")
    LSparaFrame.grid(row=0,column=0,columnspan=3)
    LSplotFrame = LabelFrame(LSFrame,text="Graphs")
    LSplotFrame.grid(row=1,column=0)


    NCFrame = LabelFrame(root,text="Novocontrol")
    NCFrame.grid(row=0,column=3)
    NCinfoFrame = LabelFrame(NCFrame,text="Sample info")
    NCinfoFrame.grid(row=0,column=0)#,columnspan=3)
    NCcompFrame = LabelFrame(NCFrame,text="Compensations")
    NCcompFrame.grid(row=0,column=1)
    NCparaFrame = LabelFrame(NCFrame,text="Parameters")
    NCparaFrame.grid(row=2,column=0,columnspan=3)
    NCoperFrame = LabelFrame(NCFrame,text="Operations")
    NCoperFrame.grid(row=4,column=0,columnspan=3)
    NCplotFrame = LabelFrame(NCFrame,text="Graphs")
    NCplotFrame.grid(row=0,column=9, rowspan=9)
    NCtextboxFrame = LabelFrame(NCFrame,text="Message")
    NCtextboxFrame.grid(row=8,column=0,columnspan=3)
    NCtextbox=Text(NCtextboxFrame, wrap=WORD, height=10, width=100)
    NCtextbox.grid(row=0,column=0)
    NCplotFrame2 = LabelFrame(NCFrame,text="More graphs")
    NCplotFrame2.grid(row=9,column=0, columnspan=10, sticky='EW')

    Button(root, text="print CSET", command=lambda: NC.print_message(LS.device.query('CSET? 1').rstrip())).grid(row=9,column=0)

    Button(root, text="Quit", command=quit).grid(row=0,column=10)
    Button(root, text="Quit", command=quit).grid(row=10,column=0)


    ### Initial Novocontrol (with textbox to feedback status)
    NC = NovocontrolInit.Novoall(rm,idn_dict,NCtextbox)


    ### Initialise data and control entries
    DataArray_initialise()

    LS_EntriesInit(LSparaFrame, LSdevice_modelNo)
    LS_Canvas = Canvas_for_plots(LSplotFrame,width=3,height=3,ncols=1,nrows=1)
    LS_Curve = Curve(LS_Canvas,0)
    LS_Canvas.initialise()
    LS_clearplot_btn = Button(LSFrame, text='Clear', command=LS_Curve.clear)
    LS_clearplot_btn.grid(row=1,column=1)



    ### Initialise graph canvas
    NC_InfoInit(NCinfoFrame)
    NC_MeaEntriesInit(NCparaFrame)
    NC_ActionsInit(NCoperFrame)
    NC_CompenEntriesInit(NCcompFrame)
    NC_Canvas = Canvas_for_plots(NCplotFrame,width=5,height=5,ncols=1,nrows=2)
    NC_Canvas.initialise()
    NC_Curve_a = Curve(NC_Canvas,0)
    NC_Curve_b = Curve(NC_Canvas,1)
    NC_Canvas2 = Canvas_for_plots(NCplotFrame2,width=5,height=2.5,ncols=2,nrows=1)
    NC_Canvas2.initialise()
    NC_Curve_c = Curve(NC_Canvas2,0)
    NC_Curve_d = Curve(NC_Canvas2,1)







    ### Start the threads
    start_time = time.time()
    threading.Thread(target=LS_continuous_monitor, args=()).start()
    threading.Thread(target=LS_continuous_renewplot, args=(LS_Curve,)).start()

    root.mainloop()		#Program is looping in this line the whole time until "Quit" is pressed

    root.destroy()	#optional, Google said it is better to have it so it is here

    
    
