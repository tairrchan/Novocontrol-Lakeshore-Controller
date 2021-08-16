import pyvisa	
import time
import datetime
import numpy as np
import ResourceManage
import re
from tkinter import *


class CustomError(Exception):
	pass
	
class Novoall():
    def __init__(self,rm,idn_dict,textbox):
        self.textbox = textbox
        #self.GPIBaddress = idn_dict['ALPHA Analyzer, Novocontrol Technologies, 6.54_400_40_736_ATBF_16012018_G3\x00']
        self.GPIBaddress = idn_dict['ALPHA Analyzer, Novocontrol Technologies, 6.71_400_40_736_ATBF_16012018_G3\x00']
        self.device = rm.open_resource(self.GPIBaddress)
        self._ACvolt = float(self.device.query('ACV?').replace('\x00','').split('=')[1])
        self._DCbias = self.device.query('DCE?').replace('\x00','').split('=')[1]
        self._DCvolt = float(self.device.query('DCV?').replace('\x00','').split('=')[1])
        self._ACfreq = float(self.device.query('GFR?').replace('\x00','').split('=')[1])
        self._wiremode = self.device.query('FRS?').replace('\x00','').split('=')[1]
        self._mode = self.device.query('MODE?').replace('\x00','').rstrip().split('=')[1]
        self._mea_integra_time = float(self.device.query('MTM?').replace('\x00','').split('=')[1])
        self._task_state = self.device.query('ZTSTAT?').replace('\x00','').split('=')
        
    @property
    def ACvolt(self):
        self._ACvolt = float(self.device.query('ACV?').replace('\x00','').split('=')[1])
        return self._ACvolt
    @ACvolt.setter
    def ACvolt(self,value):
        self.device.write('ACV=' + str(value))
            
    @property
    def DCbias(self):
        self._DCbias = self.device.query('DCE?').replace('\x00','').split('=')[1].strip()
        return self._DCbias
    @DCbias.setter
    def DCbias(self,value):
        if value in [0,1,'0','1']:
            self.device.write('DCE=' + str(value))
        else:
            raise ValueError("DCbias can only be enabled (=1) or disabled (=0).")
            
    @property
    def DCvolt(self):
        self._DCvolt = float(self.device.query('DCV?').replace('\x00','').split('=')[1])
        return self._DCvolt
    @DCvolt.setter
    def DCvolt(self,value):
        if value <= 40 or value >= -40:
            self.device.write('DCV=' + str(value))
        else:
            raise ValueError("DCvolt ranges from -40V to 40V.")

    @property
    def ACfreq(self):
        self._ACfreq = float(self.device.query('GFR?').replace('\x00','').split('=')[1])
        return self._ACfreq
    @ACfreq.setter
    def ACfreq(self,value):
        if value >= 3e-6 or value <= 4e7:
            self.device.write('GFR=' + str(value))
        else:
            raise ValueError("ACfreq ranges from 3e-6 Hz to 4e7 Hz.")
            
    @property
    def frontstate(self):
        self._frontstate = self.device.query('FRS?').replace('\x00','').split('=')[1].strip()
        return self._frontstate
    @frontstate.setter
    def frontstate(self,value):
        value = str(value)
        if value in ['2','3','4']:
            self.device.write('FRS=' + value)
        else:
            raise ValueError("Front state is only in [2,3,4]-wire mode.")

    @property
    def mode(self):
        self._mode = self.device.query('MODE?').replace('\x00','').rstrip().split('=')[1]
        return self._mode
    @mode.setter
    def mode(self,value):
        if value in ['VOLT', 'IMP', 'IMP_HV150', 'IMP_HV500', 'IMP_HV2000', 'TDM']:
            self.device.write('MODE=' + str(value))
        else:
            raise ValueError("Mode name %s is not found." %value)	

    @property
    def mea_integra_time(self):
        self._mea_integra_time = float(self.device.query('MTM?').replace('\x00','').split('=')[1])
        return self._mea_integra_time
    @mea_integra_time.setter
    def mea_integra_time(self,value):
        if value >= 0:
            self.device.write('MTM=' + str(value))
        else:
            raise ValueError("Intergartion time has to be positive number.")
            
    @property
    def task_state(self):
        self._task_state = self.device.query('ZTSTAT?').replace('\x00','').rstrip().split('=')[1].split(' ')
        #self.print_message(self.device.query('ZTSTAT?'))
        return self._task_state
        


    def print_message(self, message):
        timeObj = time.localtime(time.time())
        lastLine = self.textbox.get("%s-1l"%INSERT, INSERT)
        lastMessage = lastLine[lastLine.find('] ')+2:len(lastLine)-1]
        if lastMessage == message:
            self.textbox.delete("%s-1l"%INSERT, INSERT)
            
        self.textbox.insert(END,"[%02d:%02d:%02d] %s\n" %( timeObj.tm_hour
                                                            , timeObj.tm_min
                                                            , timeObj.tm_sec
                                                            , message))
        self.textbox.see(INSERT)



    def check_task_state(self,**kwargs):
        #print("check running")
        [task, state] = self.task_state
        time.sleep(kwargs.get('interval',0.1))
        while state == '5':
            self.print_message("State: %s, task \"%s\" is in progress" %(state,task))
            time.sleep(0.1)
            [task, state] = self.task_state			
            
        if state == '3':
            self.print_message("State: %s, task \"%s\" is successfully terminated" %(state,task))
            pass
        else:
            self.print_message("Task \"%s\" is with Status: %s. Refer to manual for description." %(task,state))
            raise CustomError("Task \"%s\" is with Status: %s. Refer to manual for description." %(task,state))
            

    def all_calibration_trigger(self):
        frontstate_buffer = self.frontstate
        self.print_message('Frontstate = %s' %self.frontstate)
        self.print_message('RST')
        self.device.write('*RST')			#Initializes the Alpha analyzer with its default values
        time.sleep(2)						#'*RST' also takes time to response but does not accept ZTSTAT? query

        
        self.print_message('ALL_INIT')
        self.device.write('ZRUNCAL=ALL_INIT')
        self.check_task_state()
        
        popup = Toplevel()
        l1 = Label(popup, text  = "Disconnect all impedance from Alpha analyzer.")
        l1.grid(row=0,column=0,columnspan=2)
        l2 = Label(popup, text  = "Four-wire Impedance Interface ZG4: ")
        l2.grid(row=1,column=0) 
        l2a = Label(popup, text  = "Remove any cables from the I high, V high, Vlow and I low terminals.")
        l2a.grid(row=1,column=1) 
        var = IntVar()
        OKbut = Button(popup, text = "OK", command = lambda: var.set(1))
        OKbut.grid(row=10,column=0,columnspan=2)
        CANCELbut = Button(popup, text = "Cancel", command = lambda: var.set(0))
        CANCELbut.grid(row=10,column=3,columnspan=2)
        popup.wait_variable(var)
        popup.destroy()
        
        if var.get() == 1:
            self.print_message('All calibration started.')
            self.print_message('ALL')
            self.device.write('ZRUNCAL=ALL')
            self.check_task_state()
            self.print_message('All calibration finished.')
            self.frontstate = frontstate_buffer     #'*RST' and 'ALL_UNIT' both reset frontstate to '2'        
            self.print_message('Frontstate = %s' %self.frontstate)
        else:
            self.print_message('All calibration aborted.')
        
    def loadshort_calibration_trigger(self):
        frontstate_buffer = self.frontstate
        self.print_message('Frontstate = %s' %self.frontstate)
        self.print_message('RST')
        self.device.write('*RST')			#Initializes the Alpha analyzer with its default values
        time.sleep(2)						#'*RST' also takes time to response but does not accept ZTSTAT? query
        self.frontstate = frontstate_buffer #'*RST' would reset frontstate to '2'
        self.print_message('Frontstate = %s' %self.frontstate)  
        
        self.print_message('SL_INIT')
        self.device.write('ZRUNCAL=SL_INIT')
        self.check_task_state()
        
        popup = Toplevel()
        l1 = Label(popup, text  = "Connect the short calibration standard to the Alpha impedance inputs.")
        l1.grid(row=0,column=0,columnspan=2)
        var = IntVar()
        OKbut = Button(popup, text = "OK", command = lambda: var.set(1))
        OKbut.grid(row=10,column=0,columnspan=2)
        CANCELbut = Button(popup, text = "Cancel", command = lambda: var.set(0))
        CANCELbut.grid(row=10,column=3,columnspan=2)

        popup.wait_variable(var)
        popup.destroy()
        
        if var.get() == 1:
            self.print_message('Short calibration started.')
            self.device.write('ZRUNCAL=SL_SHORT')
            self.check_task_state()
            self.print_message('Short calibration finished.')
            popup = Toplevel()
            l1 = Label(popup, text  = "Short calibration finished. Disconnect the short calibration standard.")
            l1.grid(row=0,column=0,columnspan=2)
            l2 = Label(popup, text  = "Connect the load calibration standard to the Alpha impedance inputs.")
            l2.grid(row=1,column=0,columnspan=2)
            var = IntVar()
            OKbut = Button(popup, text = "OK", command = lambda: var.set(1))
            OKbut.grid(row=10,column=0,columnspan=2)
            CANCELbut = Button(popup, text = "Cancel", command = lambda: var.set(0))
            CANCELbut.grid(row=10,column=3,columnspan=2)
            print(var.get())
            popup.wait_variable(var)
            popup.destroy()
            
            if var.get() == 1:
                self.print_message('Load calibration started.')
                self.device.write('ZRUNCAL=SL_100')
                self.check_task_state()
                self.print_message("Low impedance load-short calibration finished.")
                self.print_message('Frontstate = %s' %self.frontstate)
            else:
                self.print_message("Low impedance load calibration aborted.")
        else:
            self.print_message("Low impedance load-short calibration aborted.")
        
        
        
    def system_connection_check(self):
        check = self.device.query('ZCON_TO_CHECK?').replace('\x00','').split('=')[1]
        if check == '1':
            self.print_message("System connections test required before the commands ACV=, DCE= and MST can be executed")
        elif check == '0':
            self.print_message("no system connections test required")
            
    def return_V(self):
        result = self.device.query('MRE?')
        return result

    def return_Z(self):
        #global realZ,imgZ,freq,status,ref_mea_status
        result = self.device.query('ZRE?').replace('\x00','').replace('=',' ').split()
        result.pop(0)
        [realZ, imgZ, freq, status, ref_mea_status] = result
        status_dict = {'0':"Invalid (result buffer empty)"
                        ,'1':"Measurement still in progress"
                        ,'2':"Result valid"
                        ,'3':"Voltage V1 for sample measurement out of range"
                        ,'4':"Current for sample measurement out of range"
                        ,'5':"Voltage V1 for reference measurement out of range"
                        ,'6':"Analyzer signal source disconnected within measurement"}
        self.print_message('Status: %s' %status_dict[status])
        return realZ,imgZ,freq,status,ref_mea_status


    def measurement_abort(self):
        self.device.write('MBK')
        
    def measurement_trigger(self):
        if self._mode == 'IMP':
            self.device.write('MST')
        else:
            self.print_message('Measurement mode is not IMP but %s' %self._mode)
            raise CustomError('Measurement mode is not IMP but %s' %self._mode)
		
		

	

		
		
		
		
	
	# ZRE?, ZCPRE? and ZEXTRE? 

if __name__ == "__main__":
    rm = ResourceManage.rm_initiate()
    idn_dict = ResourceManage.rm_dict()
    #print(idn_dict)
    textbox = []
    Novo = Novoall(rm, idn_dict, textbox)
    #print(Novo.device.write('ZRUNCAL=ALL_INIT'))
    #print(Novo.device.write('ZRUNCAL=ALL'))
    #print(Novo.device.write('*RST'))
    #print(Novo.device.query('FRS?').replace('\x00','').split('=')[1])
    
    #Novo.device.write('DCE=1')
    #print(Novo.device.query('ZTSTAT?'))
    #Novo.DCbias = 0
    print(Novo.frontstate)
    Novo.frontstate = '4'
    print(Novo.frontstate)
    #print(Novo.device.query('DCE?').replace('\x00','').split('=')[1])
    #Novo.mea_integra_time = 0
    #print(Novo.device.query('IAU?').replace('\x00','').split('=')[1])

    #Novo.device.write('MBK')
    #print(Novo._mode == 'IMP')


	
	
	
	
	