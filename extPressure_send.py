'''
extPressure_send.py

Intakes MS5837 output and streams to control over port 5620

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
import socket
import struct

sensor = ms5837.MS5837_30BA()  # Default I2C bus is 1 (Raspberry Pi 4)
# sensor = ms5837.MS5837_30BA(0) # Specify I2C bus
# sensor = ms5837.MS5837_02BA()
# sensor = ms5837.MS5837_02BA(0)
# sensor = ms5837.MS5837(model=ms5837.MS5837_MODEL_30BA, bus=0) # Specify model and bus

# We must initialize the sensor before reading it
if not sensor.init():
    print("Sensor could not be initialized")
    exit(1)

# We have to read values from the sensor to update pressure and temperature
if not sensor.read():
    print("Sensor read failed!")
    exit(1)

freshwaterDepth = sensor.depth()  # default is freshwater
sensor.setFluidDensity(ms5837.DENSITY_SALTWATER)
saltwaterDepth = sensor.depth()  # No need to read() again
sensor.setFluidDensity(1000)  # kg/m^3
print(("Depth: %.3f m (freshwater)  %.3f m (saltwater)") % (freshwaterDepth, saltwaterDepth))

# Spew readings
def main():
    # Open TCP socket on SUB
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.2.3", 5620))  # Change the port as needed
    server_socket.listen()
    print("Reading External Depth/ Pressure and Temperature sending on port 5620")

    try:
        while True:
            client_socket, _ = server_socket.accept()
            while True:
                # read MS 5837 Data
                if sensor.read():
                    D_m = sensor.depth()
                    P_mbar = sensor.pressure()  # Default is mbar (no arguments)
                    P_psi = sensor.pressure(ms5837.UNITS_psi)  # Request psi
                    TC = sensor.temperature()  # Default is degrees C (no arguments)
                    TF = sensor.temperature(ms5837.UNITS_Farenheit)  # Request Fahrenheit
                else:
                    print("Sensor read failed!")
                    exit(1)

                extP_data = struct.pack('fffff', D_m, P_mbar, P_psi, TC, TF)
                client_socket.sendall(extP_data)
                time.sleep(1)

            client_socket.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
