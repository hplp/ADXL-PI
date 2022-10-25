import ADXL362
import time
import pandas as pd
import matplotlib.pyplot as plt

accel = ADXL362.ADXL362()
accel.begin_measure()
prog_time = 0
data = {'time' : [], 'x_accel' : [], 'y_accel' : [], 'z_accel' : [], 'temp' : []}
while prog_time < 10:
    data['time'].append(prog_time)
    data['x_accel'].append(accel.read_x())
    data['y_accel'].append(accel.read_y())
    data['z_accel'].append(accel.read_z())
    data['temp'].append(accel.read_temp())
    #print (accel.read_xyz())
    time.sleep(.01)
    prog_time += .01
    
df = pd.DataFrame.from_dict(data)
df.plot(x = 'time', y = 'x_accel', kind = 'scatter')
df.plot(x = 'time', y = 'y_accel', kind = 'scatter')
df.plot(x = 'time', y = 'z_accel', kind = 'scatter')
plt.show()
