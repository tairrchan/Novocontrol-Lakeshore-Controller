import pyvisa	
import ResourceManage
import numpy as np



class LSall():
    global channel_dict, hrange_dict
    #channel_dict = {'1':'A','A':'1','2':'B','B':'2'}
    hrange_dict = {'OFF':'0', '0':'OFF', '2.5mW':'1', '1':'2.5mW', '25mW':'2', '2':'25mW', '250mW':'3', '3':'250mW', '2.5W':'4', '4':'2.5W', '25W':'5', '5':'25W'}
    #inputcurve_dict = {'
    def __init__(self,rm,idn_dict):
        self.GPIBaddress = idn_dict['LSCI,MODEL340,340511,013102']
        self.device = rm.open_resource(self.GPIBaddress)
        self._ctrlloop = '1'
        self._channel = self.device.query('CSET? ' + self._ctrlloop).rstrip().split(',')[0]
        self.channel = self._channel    #Initialing, to configure the control loop. E.g. change unit to K and switch it on
        self._inputcurve = self.device.query('INCRV? ' + self._channel)
        self._hrange = hrange_dict[self.device.query('RANGE?').rstrip()]
        self._rampmode = float(self.device.query('RAMP? ' + self._ctrlloop).rstrip().split(',')[0])
        self._ramprate = float(self.device.query('RAMP? ' + self._ctrlloop).rstrip().split(',')[1])
        self._P = float(self.device.query('PID? ' + self._ctrlloop).rstrip().split(',')[0])
        self._I = float(self.device.query('PID? ' + self._ctrlloop).rstrip().split(',')[1])
        self._D = float(self.device.query('PID? ' + self._ctrlloop).rstrip().split(',')[2])
        self._setpoint = float(self.device.query('SETP? ' + self._ctrlloop).rstrip())
        self._nowtemp = float(self.device.query('KRDG? ' + str(self.channel)).rstrip())
        #self._nowsrdg = float(self.device.query('SRDG? ' + str(self.channel)).rstrip())
        self._houtput = float(self.device.query('HTR? ').rstrip())

    
    @property
    def channel(self):
        self._channel = self.device.query('CSET? ' + self._ctrlloop).rstrip().split(',')[0]
        return self._channel
    @channel.setter
    def channel(self, channel):
        self._channel = str(channel)
        self.device.write('CSET ' + self._ctrlloop + ',' + str(channel) + ',1,1') #',1,1' means unit=Kelvin and loop=ON respectively
        
    @property
    def inputcurve(self):
        self._inputcurve = self.device.query('INCRV? ' + self._channel)
        return self._inputcurve
    @channel.setter
    def inputcurve(self, inputcurve):
        self.device.write('INCRV ' + str(self._channel) + ',' + str(inputcurve))



    @property
    def hrange(self):
        response = self.device.query('RANGE?').rstrip()
        hrange = hrange_dict[response]
        self._hrange = hrange
        return self._hrange
    @hrange.setter
    def hrange(self,hrange):
        self.device.write('RANGE ' + hrange_dict[hrange])
        
    @property
    def rampmode(self):
        rampmode = self.device.query('RAMP? ' + self._ctrlloop).rstrip().split(',')[0]
        self._rampmode = int(rampmode)
        return self._rampmode
    @rampmode.setter
    def rampmode(self, rampmode):
        if rampmode == '1':
            self.device.write('RAMP '+ self._ctrlloop + ',' + str(rampmode) + ',' + str(self.ramprate))
        else:
            self.device.write('RAMP '+ self._ctrlloop + ',' + str(rampmode))
 
    @property
    def ramprate(self):
        ramprate = self.device.query('RAMP? ' + self._ctrlloop).rstrip().split(',')[1]
        self._ramprate = float(ramprate)
        return self._ramprate
    @ramprate.setter
    def ramprate(self, ramprate):
        if float(self.rampmode) != 0:
            self.device.write('RAMP '+ self._ctrlloop + ',' + str(self.rampmode) + ',' + str(ramprate))
        elif float(self.rampmode) == 0:
            self.device.write('RAMP '+ self._ctrlloop + ',' + str(self.rampmode))
    
    @property
    def P(self):
        P = self.device.query('PID? ' + self._ctrlloop).rstrip().split(',')[0]
        self._P = float(P)
        return self._P
    @P.setter
    def P(self,P):
        self.device.write('PID ' + self._ctrlloop + ',' + str(P) + ',' + str(self.I) + ',' + str(self.D))

    @property
    def I(self):
        I = self.device.query('PID? ' + self._ctrlloop).rstrip().split(',')[1]
        self._I = float(I)
        return self._I
    @I.setter
    def I(self,I):
        self.device.write('PID ' + self._ctrlloop + ',' + str(self.P) + ',' + str(I) + ',' + str(self.D))

    @property
    def D(self):
        D = self.device.query('PID? ' + self._ctrlloop).rstrip().split(',')[2]
        self._D = float(D)
        return self._D
    @D.setter
    def D(self,D):
        self.device.write('PID ' + self._ctrlloop + ',' + str(self.P) + ',' + str(self.I) + ',' + str(D))
    
    @property
    def setpoint(self):
        response = self.device.query('SETP? ' + self._ctrlloop).rstrip()
        self._setpoint = float(response)
        return self._setpoint
    @setpoint.setter
    def setpoint(self, setpoint):
        self.device.write('SETP ' + self._ctrlloop + ',' + str(setpoint))
        
    @property
    def nowtemp(self):
        response = self.device.query('KRDG? ' + str(self.channel)).rstrip()
        self._nowtemp = float(response)
        return self._nowtemp
        
    @property
    def nowsrdg(self):
        response = self.device.query('srdg? ' + str(self.channel)).rstrip()
        self._srdg = float(response)
        return self._srdg

    @property
    def houtput(self):
        response = self.device.query('HTR? ' + str(self.channel)).rstrip()
        self._houtput = float(response)
        return self._houtput
		
    def configCurve(self,curveDataFile,curveNo):
        df = np.loadtxt(curveDataFile,skiprows=2)
        for i in range(len(df)):
	        cmd = 'CRVPT ' + str(curveNo) + ',' + str(i+1) + ',' + str(round(df[i][1],4)) + ',' + str(round(df[i][0],4))
	        print(cmd)
	        self.device.query(cmd)
        return



    

if __name__ == "__main__":

    rm = ResourceManage.rm_initiate()
    idn_dict = ResourceManage.rm_dict()
    print(idn_dict)
    LS = LSall(rm,idn_dict)


    #print(LS.nowtemp)
    #LS.setpoint = '300'

    #print(LS.device.query('CRVDEL 42'))
    #print(LS.device.query('CRVHDR? 42'))
    #print(LS.device.query('CRVHDR 42,Cernox,X-142027,3,310.0,1'))
    #print(LS.device.query('CRVHDR? 42'))



    #### Load temperature curve calibrated data points

    #curveDataFile = r"\\S4\Datenpool\Yuk Tai\Python\Cenox calibration curve\X142027\X142027.dat"
    #LS.configCurve(curveDataFile,42)
    #curveDataFile = r"\\S4\Datenpool\Dielectric group\Temperature sensor calibration curves\Cenox calibration curve\Cernox_Default_NotStandard.dat"
    #LS.configCurve(curveDataFile,43)   
        
    
        
    #print(LS.device.query('CRVHDR? 43'))
    #print(LS.device.query('CRVHDR 43, Cernox, Default, 3, 500, 1'))
    #print(LS.device.query('CRVHDR? 43'))
