from pyubx2 import UBXReader
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
import pickle


start_time = time.time() 

# Dictionary to keep track of each satellite C/N0 for the .ubx file
satellite_data = {}

# Parse UBX messages and filer only RXM-RAWX messages to process
#file_path = "C:/Users/hjy23/OneDrive - Stanford/GPS lab LCM/Jammer test/lcm0003_20240815_12.ubx"
file_path = "C:/Users/hjy23/OneDrive - Stanford/GPS lab LCM/Jammer test/20240909/LCM/L1L5mb01_ubxlog_12.ubx"


with open(file_path, "rb") as f:

    ubr = UBXReader(f)  
    for (raw_data, parsed_data) in ubr:
        if parsed_data == None:
            print('invalid data') # rarely happens but broke code once, just in case
            continue
        if parsed_data.identity == "RXM-RAWX":
            # Extract receiver time of week

            #break # for if i'm looking at an example parsed_data of "RXM-RAWX"
            
            time_of_week = parsed_data.rcvTow  # Time in seconds
            
            # Loop through everything in RXM-RAWX
            num_sats = parsed_data.numMeas  # Number of satellite observations from the message
            for i in range(1, num_sats + 1):
                # Extract gnssId, svId, sigId, and C/N0 for each satellite
                gnss_id = getattr(parsed_data, f"gnssId_{i}", None)
                
                sig_id = getattr(parsed_data, f"sigId_{i}", None)  # Frequency band
                
                
                #filter out only GPS L1 and GALLILEO E1 for our analysis
                if (gnss_id == 0 and sig_id == 0) or (gnss_id == 2 and sig_id == 0):
                    
                    sv_id = getattr(parsed_data, f"svId_{i}", None)
                    
                    cno = getattr(parsed_data, f"cno_{i}", None)       # C/N0 value
        
                    # Skip if no valid data (pretty rare)
                    if gnss_id is None or sv_id is None or cno is None:
                        continue
                    
                    # what's used to identify the satettlite and its signal
                    sat_key = (gnss_id, sv_id, sig_id)
                    
                    # initializatew if we don't have the satellite in view
                    if sat_key not in satellite_data:
                        satellite_data[sat_key] = {"times": [], "cno_values": []}
                    
                    # Append time and C/N0 value to the satellite's data
                    satellite_data[sat_key]["times"].append(time_of_week)
                    satellite_data[sat_key]["cno_values"].append(cno)
    
    
# Save the satellite_data dictionary because each run takes so long
# then I can load the dictionary whenever I want to do data processing
with open("satellite_data.pkl", "wb") as file:
    pickle.dump(satellite_data, file)

end_time=time.time()
elapsed_time = end_time - start_time

###for reference
###one hour of data took 140 seconds to run (a litle over 2 minutes)
###a whole day of data took 487 seconds(8 minutes) to run 20240909 L1L2mb04