import os
import pandas as pd

# Set the directory paths for the input and output files
input_folder = '/Users/carsenhobson/Downloads/carson_pa/'
output_folder = '/Users/carsenhobson/Downloads/carson_pa_output/'

# Create the output directory if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Get the list of files in the directory
files = os.listdir(input_folder)

# Sort the files based on their order in the file system
data_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(input_folder, x)))


# Iterate over each pair of data files
for i in range(0, len(data_files),2):
    # Get the file names for the pair
    indoor_file = data_files[i]
    outdoor_file = data_files[i + 1]

    # Read the indoor and outdoor data files
    indoor_data = pd.read_csv(os.path.join(input_folder, indoor_file))
    outdoor_data = pd.read_csv(os.path.join(input_folder, outdoor_file))

    # Convert 'created_at' column to datetime format
    indoor_data['created_at'] = pd.to_datetime(indoor_data['created_at'])
    outdoor_data['created_at'] = pd.to_datetime(outdoor_data['created_at'])

    # Calculate the means of indoor and outdoor PM2.5 levels
    indoor_mean = indoor_data['PM2.5_CF1_ug/m3'].mean()
    outdoor_mean = outdoor_data['PM2.5_CF1_ug/m3'].mean()

    # Calculate the spike thresholds
    spike_threshold_indoor = indoor_mean + 5
    spike_threshold_outdoor = outdoor_mean + 5

    # Merge the indoor and outdoor data based on the timestamp
    merged_data = indoor_data.merge(outdoor_data, on='created_at', suffixes=('_indoor', '_outdoor'))

    # Identify spikes when both indoor and outdoor PM2.5 levels exceed the thresholds
    spike_data = merged_data[(merged_data['PM2.5_CF1_ug/m3_indoor'] > spike_threshold_indoor) & (merged_data['PM2.5_CF1_ug/m3_outdoor'] > spike_threshold_outdoor)]

    # Calculate the duration of each peak
    spike_data['duration'] = spike_data['created_at'].diff().fillna(pd.Timedelta(seconds=0))

     # Calculate the average duration of spikes
    average_duration = spike_data['duration'].mean()

    # Add the average duration column
    spike_data['average_duration'] = average_duration
     
     # Exclude peaks with a duration of zero time
    spike_data = spike_data[spike_data['duration'] != pd.Timedelta(seconds=0)]
    
    # Generate unique file name for each pair
    output_file = 'spike_data_' + indoor_file.replace('.csv', '_') + outdoor_file

    # Save the spike data to a CSV file in the output directory
    spike_data[['entry_id_indoor', 'created_at', 'PM2.5_CF1_ug/m3_indoor', 'entry_id_outdoor', 'PM2.5_CF1_ug/m3_outdoor', 'duration','average_duration']].to_csv(os.path.join(output_folder, output_file), index=False)
