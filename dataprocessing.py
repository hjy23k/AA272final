import pickle
import matplotlib.pyplot as plt
import numpy as np
import pickle

# Load the dictionary with C/n values
with open("C:/Users/hjy23/OneDrive - Stanford/GPS lab LCM/Jammer test/satellite_data.pkl", "rb") as file:
    satellite_data = pickle.load(file)


#just the GNSSID described in UBX documentation
def get_gnss_name(gnss_id):
    """Map GNSS ID to the GNSS constellation name."""
    gnss_map = {
        0: 'GPS',
        1: 'SBAS',
        2: 'GALILEO',
        3: 'BEIDOU',
        4: 'IMES',
        5: 'QZSS',
        6: 'GLONASS',
        7: 'NavIC'
    }
    return gnss_map.get(gnss_id)


from collections import defaultdict

def compute_average_cno_efficient(satellite_data):
    """
    Computes the average C/N₀ across all satellites (in the dictionary) with valid data for each time step.

    Args:
        satellite_data (dict): Dictionary containing satellite data with 'times' and 'cno_values'.

    Returns:
        dict: A dictionary where the key is the time, and the value is the average C/N₀ at that time.
    """
    # Use defaultdict to aggregate C/N₀ values by time
    cno_aggregator = defaultdict(list)

    for data in satellite_data.values():
        times = np.array(data['times'])
        cno_values = np.array(data['cno_values'])

        for t, cno in zip(times, cno_values):
            if not np.isnan(cno):  # Skip invalid values
                cno_aggregator[t].append(cno)

    # Compute the average C/N₀ for each time
    avg_cno_dict = {time: np.mean(cnos) for time, cnos in cno_aggregator.items()}

    return avg_cno_dict


def plot_average_cno(average_cno_list):
    """
    Plots the average C/N₀ that we calculated above over time.
    """
    # Separate the list of tuples into two lists: times and average C/N₀ values
    times, avg_cno_values = zip(*average_cno_list)

    # Plot the data
    plt.figure(figsize=(12, 6))
    plt.plot(times, avg_cno_values, marker='o', markersize = 0, label='Average C/N₀')
    
    
    #change this line below!!!! for the correct date
    plt.title("2024/09/09 Rx4 average C/N₀", fontsize=16)
    
    plt.xlabel("Time (rcvTow in seconds)", fontsize=14)
    plt.ylabel("Average C/N₀ (dB-Hz)", fontsize=14)
    plt.grid(True)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()




def plot_all_satellites(satellite_data):
#this function plots all satellites and their C/N = instead of an average
    
    plt.figure(figsize=(15, 10))
    for (gnss_id, satellite_id, signal_id), data in satellite_data.items():
        times = np.array(data['times'])
        cno_values = np.array(data['cno_values'])


        # Filter data to include only times between `start_time` and `end_time`
        gnss_name = get_gnss_name(gnss_id)
        label = f"{gnss_name} Sat {satellite_id} Sig {signal_id}"
        plt.plot(times, cno_values, label=label)
    
    plt.title("2024/09/09 Rx4 C/N₀ of L1/E1 Satellites", fontsize=16)
    plt.xlabel("Time (rcvTow in seconds)", fontsize=14)
    plt.ylabel("C/N₀ (dB-Hz)", fontsize=14)
    plt.legend(fontsize=8, loc='upper right', bbox_to_anchor=(1.3, 1))
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_all_satellites_duration(satellite_data):
    duration = 1000
    
    plt.figure(figsize=(15, 10))
    start_time = 9999999999
    end_time = 0
    for (gnss_id, satellite_id, signal_id), data in satellite_data.items():
        if min(data['times']) < start_time:
            start_time = min(data['times'])
        if max(data['times']) > end_time:
            end_time = max(data['times'])
    
    limit_time = start_time + duration
    time_points = []  # To store unique time steps
    for (gnss_id, satellite_id, signal_id), data in satellite_data.items():
        times = np.array(data['times'])
        cno_values = np.array(data['cno_values'])

        # Skip satellites that only have data after the end time
        if times[0] > limit_time:
            continue

        # Filter data to include only times between `start_time` and `end_time`
        valid_indices = (times >= start_time) & (times <= limit_time)
        
        
        times = times[valid_indices]
        cno_values = cno_values[valid_indices]

        if len(times) == 0:
            continue  # Skip plotting if no data exists in the time range
        # Use the GNSS name instead of just the ID
        gnss_name = get_gnss_name(gnss_id)
        label = f"{gnss_name} Sat {satellite_id} Sig {signal_id}"
        plt.plot(times, cno_values, label=label)
    
    plt.title("2024/09/09 Rx4 C/N₀ of L1/E1 Satellites", fontsize=16)
    plt.xlabel("Time (rcvTow in seconds)", fontsize=14)
    plt.ylabel("C/N₀ (dB-Hz)", fontsize=14)
    plt.legend(fontsize=8, loc='upper right', bbox_to_anchor=(1.3, 1))
    plt.grid(True)
    plt.tight_layout()
    plt.show()



def plot_moving_average(average_cno_list, window_size=3):
    """
    Computes the smoothed average C/N₀ values

    takes in the average c/n list and a window size
    default window size is set to 3
    """
    # Separate the list of tuples into two lists: times and average C/N₀ values
    times, avg_cno_values = zip(*average_cno_list)
    avg_cno_values = np.array(avg_cno_values)

    # Compute the moving average
    moving_avg_cno = np.convolve(avg_cno_values, np.ones(window_size) / window_size, mode='valid')

    # Adjust time array for moving average (to match the size of 'valid' mode)
    adjusted_times = times[(window_size - 1) // 2 : -(window_size - 1) // 2 or None]

    # Plot the data
    plt.figure(figsize=(12, 6))
    plt.plot(times, avg_cno_values, label="Raw Average C/N₀", alpha=0.6)
    plt.plot(adjusted_times, moving_avg_cno, label=f"Smoothing (Window: {window_size})", color="red")
    plt.title("2024/09/09 Rx4 smoothed average C/N₀", fontsize=16)
    plt.xlabel("Time (rcvTow in seconds)", fontsize=14)
    plt.ylabel("Average C/N₀ (dB-Hz)", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

plot_all_satellites(satellite_data)

plot_all_satellites_duration(satellite_data)


average_cno_dict = compute_average_cno_efficient(satellite_data)

# Convert the dictionary to a sorted list
average_cno_list = sorted(average_cno_dict.items())

plot_average_cno(average_cno_list[:])
#average_cno_list = compute_average_cno_list(satellite_data)

plot_moving_average(average_cno_list, window_size=5)

##also save the average cno list as well for possible future processing
output_file = "average_cno_list.pkl"
with open(output_file, "wb") as file:
    pickle.dump(average_cno_list, file)


average = 0
count = 0
for i in average_cno_list[16000:16100]:
    average += i[1]
    count += 1
print(average/count)


