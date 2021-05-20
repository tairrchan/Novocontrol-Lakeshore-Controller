import numpy as np

def FlushPlot(Curve_object):
	if Curve_object._xData.size > 0:
		Curve_object._curve.set_xdata(Curve_object._xData)
		Curve_object._curve.set_ydata(Curve_object._yData)
		minX = np.min(Curve_object._xData)
		maxX = np.max(Curve_object._xData)
		minY = np.min(Curve_object._yData)
		maxY = np.max(Curve_object._yData)
		if Curve_object._xData.size > 5:
			data_yRange = maxY - minY
			data_xRange = maxX - minX
			if Curve_object._ax.get_xaxis().get_scale() == 'log':
				posXData = Curve_object._xData[np.where(Curve_object._xData > 0)]
				if posXData.size != 0:
					minX = np.min(posXData)
					Curve_object._ax.set_xlim(10**(np.log10(minX)-0.01*np.log10(data_xRange)),10**(np.log10(maxX)+0.01*np.log10(data_xRange)))
				else:
					pass
			else:
				Curve_object._ax.set_xlim(minX-0.01*data_xRange,maxX+0.01*data_xRange)
				
			if Curve_object._ax.get_yaxis().get_scale() == 'log':	
				posYData = Curve_object._yData[np.where(Curve_object._yData > 0)]
				if posYData.size != 0:
					minY = np.min(posYData)
					Curve_object._ax.set_ylim(10**(np.log10(minY)-0.01*np.log10(data_yRange)),10**(np.log10(maxY)+0.01*np.log10(data_yRange)))
				else:
					pass
				
			else:	
				Curve_object._ax.set_ylim(minY-0.01*data_yRange,maxY+0.01*data_yRange)
		else:
			Curve_object._ax.set_xlim(0.99*minX,1.01*maxX)
			Curve_object._ax.set_ylim(0.99*minY,1.01*maxY)
		Curve_object._Canvas._fig.canvas.flush_events()
	else:
		pass
		
		
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
		
	
	
		
		
		
		
		
		
		
		
		