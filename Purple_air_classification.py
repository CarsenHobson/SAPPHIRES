import os
import pandas as pd

# Set the directory paths for the input and output files
input_folder = '/Users/carsenhobson/Downloads/carson_pa2/'
output_folder = '/Users/carsenhobson/Downloads/carson_pa_output_classification/'

# Create the output directory if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Get the list of files in the directory
files = os.listdir(input_folder)

# Sort the files based on their order in the file system
data_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(input_folder, x)))

# Iterate over each pair of data files
for i in range(0, len(data_files), 2):
    # Check if there is a corresponding outdoor file available
    if i + 1 >= len(data_files):
        break

    # Get the file names for the pair
    indoor_file = data_files[i]
    outdoor_file = data_files[i + 1]

    # Read the indoor and outdoor data files
    indoor_data = pd.read_csv(os.path.join(input_folder, indoor_file))
    outdoor_data = pd.read_csv(os.path.join(input_folder, outdoor_file))

    # Calculate the means of indoor and outdoor PM2.5 levels
    indoor_mean = indoor_data['PM2.5_CF1_ug/m3'].mean()
    outdoor_mean = outdoor_data['PM2.5_CF1_ug/m3'].mean()

    # Classify the data based on PM2.5 levels
    def classify(row):
        indoor_threshold = indoor_mean + 5
        outdoor_threshold = outdoor_mean + 5

        indoor_pm25 = row['PM2.5_CF1_ug/m3_indoor']
        outdoor_pm25 = row['PM2.5_CF1_ug/m3_outdoor']

        if indoor_pm25 > indoor_threshold and outdoor_pm25 > outdoor_threshold:
            return 4  # Both indoor and outdoor elevated
        elif indoor_pm25 > indoor_threshold:
            return 2  # Inside elevated, outside not elevated
        elif outdoor_pm25 > outdoor_threshold:
            return 3  # Outside elevated, inside not elevated
        else:
            return 1  # Neither elevated

    # Merge the indoor and outdoor data based on the timestamp
    merged_data = indoor_data.merge(outdoor_data, on='created_at', suffixes=('_indoor', '_outdoor'))

    # Classify the data and add the 'classification' column
    merged_data['classification'] = merged_data.apply(classify, axis=1)

    # Keep only relevant columns for the classification data
    classification_data = merged_data[['entry_id_indoor', 'created_at', 'PM2.5_CF1_ug/m3_indoor', 'entry_id_outdoor', 'PM2.5_CF1_ug/m3_outdoor', 'classification']]

    # Save the classified data to a new CSV file
    output_file = f'classification_{indoor_file}'
    classification_data.to_csv(os.path.join(output_folder, output_file), index=False)

