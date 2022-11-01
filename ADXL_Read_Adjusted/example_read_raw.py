import ADXL362
import time
import pandas as pd
import matplotlib.pyplot as plt

accel = ADXL362.ADXL362()
accel.begin_measure()
print(accel.check_all_regs())
prog_time = 0
data = {'time' : [], 'x_accel' : [], 'y_accel' : [], 'z_accel' : [], 'temp' : []}
while prog_time < 10:
    print(accel.read_xyz())
    data['time'].append(prog_time)
    data['x_accel'].append(accel.read_x())#*(2.048 * 2 / 2 ** 20))
    data['y_accel'].append(accel.read_y())#*(2.048 * 2 / 2 ** 20))
    data['z_accel'].append(accel.read_z())#*(2.048 * 2 / 2 ** 20))
    data['temp'].append(accel.read_temp())
    #print (accel.read_xyz())
    time.sleep(.1)
    prog_time += .1
    
df = pd.DataFrame.from_dict(data)
df.to_csv('vibration.csv')
df.plot(x = 'time', y = 'x_accel', kind = 'scatter')
df.plot(x = 'time', y = 'y_accel', kind = 'scatter')
df.plot(x = 'time', y = 'z_accel', kind = 'scatter')
plt.show()
