import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def fetch_data(db_path, table_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    # Retrieve data from the specified table
    data_query = f"SELECT * FROM {table_name};"
    data = pd.read_sql_query(data_query, conn)
    # Close the database connection
    conn.close()
    return data

# Define paths to your databases and the table name
db_paths = [
    '/Users/carsenhobson/Downloads/aerosolchambercasetests/air_quality(main case).db',
    '/Users/carsenhobson/Downloads/aerosolchambercasetests/air_quality(small case).db',
    '/Users/carsenhobson/Downloads/aerosolchambercasetests/air_quality(no case).db',
    '/Users/carsenhobson/Downloads/pm25.db'
]
table_name = 'air_quality'

# Fetch data from each database
data1 = fetch_data(db_paths[0], table_name)
data2 = fetch_data(db_paths[1], table_name)
data3 = fetch_data(db_paths[2], table_name)
data4 = fetch_data(db_paths[3], table_name)

# Convert the 'timestamp' column to datetime
data1['timestamp'] = pd.to_datetime(data1['timestamp'])
data2['timestamp'] = pd.to_datetime(data2['timestamp'])
data3['timestamp'] = pd.to_datetime(data3['timestamp'])
data4['timestamp'] = pd.to_datetime(data4['timestamp'])

# Plot the data
plt.figure(figsize=(14, 7))

plt.plot(data1['timestamp'], data1['pm2_5'], label='Main case - PM2.5 Levels', color='blue')
plt.plot(data2['timestamp'], data2['pm2_5'], label='Small case - PM2.5 Levels', color='green')
plt.plot(data3['timestamp'], data3['pm2_5'], label='No case - PM2.5 Levels', color='red')
plt.plot(data4['timestamp'], data4['pm2_5'], label='Main case - PM2.5 Levels', color='blue')

# Format the x-axis to show readable date labels
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=10))

plt.xlabel('Timestamp')
plt.ylabel('PM2.5 Levels')
plt.title('PM2.5 Levels Overlayed from case tests')
plt.legend()
plt.grid(True)
plt.xticks(rotation=0)  # Rotate x-axis labels for better readability
plt.show()
