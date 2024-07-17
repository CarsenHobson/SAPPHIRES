import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the SQLite database
db_path = '/Users/carsenhobson/Downloads/detectiontest.db'  # Replace with the actual path to your database
conn = sqlite3.connect(db_path)

# Get table names
query = "SELECT name FROM sqlite_master WHERE type='table';"
tables = pd.read_sql_query(query, conn)
print(tables)

# Assuming you know the table you want to query, replace 'your_table_name' with the actual table name
table_name = 'detectiontestV2'  # Replace with the actual table name

# Retrieve data from the specified table
data_query = f"SELECT * FROM {table_name};"
data = pd.read_sql_query(data_query, conn)

# Display the first few rows of the data to understand its structure
print(data.head())

# Convert timestamps to datetime if necessary (assuming 'timestamp' column is present)
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='s')

# Plot the data
plt.figure(figsize=(14, 7))

# Assuming you have columns 'pm25', 'baselinepm25', and 'relaystate' in your data
plt.plot(data['timestamp'], data['pm25'], label='PM2.5 Levels', color='blue')
plt.plot(data['timestamp'], data['baselinepm25'], label='Baseline PM2.5 Levels', color='green')

# Highlight when relay is ON
relay_on = data[data['relaystate'] == 'ON']
plt.scatter(relay_on['timestamp'], relay_on['pm25'], color='red', label='Relay ON', s=10)

# Set x-axis and y-axis limits
plt.xlim(pd.Timestamp('2024-07-04'), pd.Timestamp('2024-07-06'))  # Set your desired x-axis limits
plt.ylim(0,50)
plt.xlabel('Timestamp')
plt.ylabel('PM2.5 Levels')
plt.title('PM2.5 Levels, Baseline and Relay State')
plt.legend()
plt.grid(True)
plt.show()

# Close the database connection
conn.close()
