import pyvisa	
import ResourceManage



class LSall():
	global channel_dict, hrange_dict
	channel_dict = {'1':'A','A':'1','2':'B','B':'2'}
	hrange_dict = {'OFF':'0', '0':'OFF', 'LOW':'1', '1':'LOW', 'MED':'2', '2':'MED', 'HIGH':'3', '3':'HIGH'}

	def __init__(self,rm,idn_dict):
		self.GPIBaddress = idn_dict['LSCI,MODEL336,LSA165V/#######,2.7']
		self.device = rm.open_resource(self.GPIBaddress)
		self._channel = channel_dict[self.device.query('OUTMODE? 1').split(',')[1]]
		self._hrange = hrange_dict[self.device.query('RANGE?').rstrip()]
		self._rampmode = float(self.device.query('RAMP?').rstrip().split(',')[0])
		self._ramprate = float(self.device.query('RAMP?').rstrip().split(',')[1])
		self._P = float(self.device.query('PID?').rstrip().split(',')[0])
		self._I = float(self.device.query('PID?').rstrip().split(',')[1])
		self._D = float(self.device.query('PID?').rstrip().split(',')[2])
		self._setpoint = float(self.device.query('SETP?').rstrip())
		self._nowtemp = float(self.device.query('KRDG? ' + str(self.channel)).rstrip())
		self._houtput = float(self.device.query('HTR? ' + str(self.channel)).rstrip())

	@property
	def channel(self):
		response = self.device.query('OUTMODE? 1').split(',')[1]
		channel = channel_dict[response]
		self._channel = channel
		return self._channel
	@channel.setter
	def channel(self, channel):
		self.device.write('OUTMODE 1,1,' + str(channel) + ',1')
		
	@property
	def hrange(self):
		response = self.device.query('RANGE?').rstrip()
		hrange = hrange_dict[response]
		self._hrange = hrange
		return self._hrange
	@hrange.setter
	def hrange(self,hrange):
		self.device.write('RANGE 1,' + hrange_dict[hrange])
		
	@property
	def rampmode(self):
		rampmode = self.device.query('RAMP?').rstrip().split(',')[0]
		self._rampmode = int(rampmode)
		return self._rampmode
	@rampmode.setter
	def rampmode(self, rampmode):
		if rampmode == 1:
			self.device.write('RAMP 1,' + str(rampmode) + ',' + str(self.ramprate))
		else:
			self.device.write('RAMP 1,' + str(rampmode))
			
	@property
	def ramprate(self):
		ramprate = self.device.query('RAMP?').rstrip().split(',')[1]
		self._ramprate = float(ramprate)
		return self._ramprate
	@ramprate.setter
	def ramprate(self, ramprate):
		if float(self.rampmode) != 0:
			self.device.write('RAMP 1,' + str(self.rampmode) + ' ' + str(ramprate))
		elif float(self.rampmode) == 0:
			self.device.write('RAMP 1,' + str(self.rampmode))
			
	@property
	def P(self):
		P = self.device.query('PID?').rstrip().split(',')[0]
		self._P = float(P)
		return self._P
	@P.setter
	def P(self,P):
		self.device.write('PID 1,' + str(P) + ',' + str(self.I) + ',' + str(self.D))

	@property
	def I(self):
		I = self.device.query('PID?').rstrip().split(',')[1]
		self._I = float(I)
		return self._I
	@I.setter
	def I(self,I):
		self.device.write('PID 1,' + str(self.P) + ',' + str(I) + ',' + str(self.D))

	@property
	def D(self):
		D = self.device.query('PID?').rstrip().split(',')[2]
		self._D = float(D)
		return self._D
	@D.setter
	def D(self,D):
		self.device.write('PID 1,' + str(self.P) + ',' + str(self.I) + ',' + str(D))

	@property
	def setpoint(self):
		response = self.device.query('SETP?')
		self._setpoint = float(response)
		return self._setpoint
	@setpoint.setter
	def setpoint(self, setpoint):
		self.device.write('SETP 1,' + str(setpoint))
		
	@property
	def nowtemp(self):
		response = self.device.query('KRDG? ' + str(self.channel)).rstrip()
		self._nowtemp = float(response)
		return self._nowtemp
	
	@property
	def houtput(self):
		response = self.device.query('HTR? ' + str(self.channel)).rstrip()
		self._houtput = float(response)
		return self._houtput


if __name__ == "__main__":

    rm = ResourceManage.rm_initiate()
    idn_dict = ResourceManage.rm_dict()

    LS = LSall(rm,idn_dict)

    #print(LS.ramprate)



