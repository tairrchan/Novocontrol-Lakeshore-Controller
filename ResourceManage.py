import pyvisa

def rm_initiate():
	global rm
	rm = pyvisa.ResourceManager()
	return rm


def rm_dict():
    global rmList, idn_list
    rmList = rm.list_resources()
    #print(rmList)
    idn_dict = {}
    for i in rmList: 
        if 'GPIB' in i:
            idn = rm.open_resource(i).query('*IDN?').rstrip()
            idn_dict[idn] = i
    return idn_dict
	
	
if __name__ == "__main__":
    rm = rm_initiate()
    rm_dict = rm_dict()
    #print(rm_dict)
    #print(rm_dict['LSCI,MODEL340,340511,013102'])
        
    GPIBaddress = rm_dict['LSCI,MODEL340,340511,013102']
    device = rm.open_resource(GPIBaddress)
    
    print(device.query('CSET? 1'))
    device.write('CSET 1, A, 1, 1')
    print(device.query('CSET? 1').rstrip().split(','))
    device.write('PID 1,100,30,5')
    print(device.query('PID? 1'))
 
    