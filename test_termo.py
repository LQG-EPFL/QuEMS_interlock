import piplates.THERMOplate as THERMO

import time

while True:
	for tid in range(11):
		tid += 1
		print (THERMO.getTEMP(2, tid))
		time.sleep(0.01)
	
	time.sleep(1)
