import sqlite3
import sys  # Import sys to allow the script to exit

# Database file path
db_file = 'your_database_file.db'  # Replace with your actual database file path

def check_filter_state_on():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Check if any 'filter_state' value is set to 'ON'
    cursor.execute('''
        SELECT 1 FROM pm25_data WHERE filter_state = "ON" LIMIT 1
    ''')
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    # If result is not None, that means at least one entry with filter_state "ON" exists
    if result:
        print("Filter state is ON. Exiting the script.")
        sys.exit()

def get_last_60_pm25_values():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Fetch the last 60 PM2.5 values (sorted by timestamp in descending order)
    cursor.execute('''
        SELECT pm25_value FROM pm25_data
        ORDER BY timestamp DESC
        LIMIT 60
    ''')
    results = cursor.fetchall()

    # Close the connection
    conn.close()

    # Return a list of the PM2.5 values (ignoring the SQL tuples)
    return [row[0] for row in results]

def calculate_average(values):
    if not values:
        return 0.0
    return sum(values) / len(values)

def update_baseline_with_average(average_value):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Update the baseline column with the calculated average for all entries
    cursor.execute('''
        UPDATE pm25_data
        SET baseline = ?
    ''', (average_value,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def main():
    # Step 1: Check if any filter_state is "ON", and exit if true
    check_filter_state_on()

    # Step 2: Get the last 60 PM2.5 values
    pm25_values = get_last_60_pm25_values()

    # Step 3: Calculate the average of those values
    average_pm25 = calculate_average(pm25_values)

    # Step 4: Update the baseline with the calculated average
    update_baseline_with_average(average_pm25)

if __name__ == '__main__':
    main()
