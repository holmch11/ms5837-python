'''
logpressure.py

Intakes MS5837 Data output and streams to file

Copyright (c) 2023
Created by Christopher Holm
holmch@oregonstate.edu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Revision History
#####################################################################################
2023/01/04 CEH Initial Version


####################################################################################
'''
#!/usr/bin/python
import ms5837
import time
import datetime
import csv

sensor = ms5837.MS5837_30BA() # Default I2C bus is 1 (Raspberry Pi 4)
#sensor = ms5837.MS5837_30BA(0) # Specify I2C bus
#sensor = ms5837.MS5837_02BA()
#sensor = ms5837.MS5837_02BA(0)
#sensor = ms5837.MS5837(model=ms5837.MS5837_MODEL_30BA, bus=0) # Specify model and bus

# We must initialize the sensor before reading it
if not sensor.init():
        print("Sensor could not be initialized")
        exit(1)

# We have to read values from sensor to update pressure and temperature
if not sensor.read():
    print("Sensor read failed!")
    exit(1)

print(("Pressure: %.2f atm  %.2f Torr  %.2f psi") % (
sensor.pressure(ms5837.UNITS_atm),
sensor.pressure(ms5837.UNITS_Torr),
sensor.pressure(ms5837.UNITS_psi)))

print(("Temperature: %.2f C  %.2f F  %.2f K") % (
sensor.temperature(ms5837.UNITS_Centigrade),
sensor.temperature(ms5837.UNITS_Farenheit),
sensor.temperature(ms5837.UNITS_Kelvin)))

freshwaterDepth = sensor.depth() # default is freshwater
sensor.setFluidDensity(ms5837.DENSITY_SALTWATER)
saltwaterDepth = sensor.depth() # No nead to read() again
sensor.setFluidDensity(1000) # kg/m^3
print(("Depth: %.3f m (freshwater)  %.3f m (saltwater)") % (freshwaterDepth, saltwaterDepth))

# fluidDensity doesn't matter for altitude() (always MSL air density)
print(("MSL Relative Altitude: %.2f m") % sensor.altitude()) # relative to Mean Sea Level pressure in air

time.sleep(5)

# Spew readings
while True:
    if sensor.read():
        pressure = sensor.pressure()
        psi_pressure = sensor.pressure(ms5837.UNITS_psi)
        temperature = sensor.temperature()
        fahrenheit_temperature = sensor.temperature(ms5837.UNITS_Farenheit)
        time.sleep(1)
        # Create a datestamped file name
        now = datetime.datetime.now()
        file_name = "/home/turtlecam/pressure/pressure" + now.strftime("%Y-%m-%d") + ".csv"

        # Append the data to the file
        with open(file_name, "a", newline='') as file:
            writer = csv.writer(file)
            # Write header if file is empty
            if file.tell() == 0:
                writer.writerow(["Timestamp", "Pressure (mbar)", "Pressure (psi)", "Temperature (C)", "Temperature (F)"])
            writer.writerow([now.strftime('%Y-%m-%d %H:%M:%S'), pressure, psi_pressure, temperature, fahrenheit_temperature])
    else:
        print("Sensor read failed!")
        exit(1)
