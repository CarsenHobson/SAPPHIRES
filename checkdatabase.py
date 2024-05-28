import sqlite3

DATABASE_NAME = "mqtt_data.db"

def print_table_contents():
    """Print the contents of each table in the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    tables = ["ZeroW1", "ZeroW2", "ZeroW3", "ZeroW4"]
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        print(f"Contents of {table}:")
        for row in rows:
            print(row)
        print("-" * 40)

    conn.close()

if __name__ == '__main__':
    print_table_contents()
