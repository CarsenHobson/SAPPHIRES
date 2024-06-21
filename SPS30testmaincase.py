import time
import sqlite3
import threading
from sps30 import SPS30
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Function to initialize the SQLite database
def initialize_db():
    conn = sqlite3.connect('air_quality.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS air_quality
                 (timestamp TEXT, pm2_5 REAL)''')
    conn.commit()
    conn.close()

# Function to log PM2.5 data to the SQLite database
def log_data(pm2_5):
    conn = sqlite3.connect('air_quality.db')
    c = conn.cursor()
    c.execute("INSERT INTO air_quality (timestamp, pm2_5) VALUES (datetime('now'), ?)", (pm2_5,))
    conn.commit()
    conn.close()

# Function to read data from the SPS30 sensor continuously
def read_sps30():
    sensor = SPS30(1)  # 1 indicates the I2C bus number
    sensor.start_measurement()
    time.sleep(2)  # Wait for the first measurement to be ready

    try:
        while True:
            data = sensor.get_measurement()
            if data:
                pm2_5 = data['pm2.5']
                print(f"PM2.5 Level: {pm2_5} µg/m³")
                log_data(pm2_5)
            time.sleep(1)  # Read data every second
    except KeyboardInterrupt:
        print("Measurement stopped by user.")
    finally:
        sensor.stop_measurement()

# Function to fetch the latest PM2.5 data from the SQLite database
def fetch_latest_data():
    conn = sqlite3.connect('air_quality.db')
    c = conn.cursor()
    c.execute("SELECT timestamp, pm2_5 FROM air_quality ORDER BY timestamp DESC LIMIT 10")
    data = c.fetchall()
    conn.close()
    return data

# Initialize the SQLite database
initialize_db()

# Start the data reading thread
threading.Thread(target=read_sps30, daemon=True).start()

# Initialize Dash app
app = Dash(__name__)
app.layout = html.Div([
    html.H1("PM2.5 Real-Time Dashboard"),
    dcc.Graph(id='pm25-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # in milliseconds
        n_intervals=0
    )
])

@app.callback(Output('pm25-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    data = fetch_latest_data()
    timestamps = [row[0] for row in data]
    pm2_5_values = [row[1] for row in data]

    figure = {
        'data': [go.Scatter(
            x=timestamps,
            y=pm2_5_values,
            mode='lines+markers'
        )],
        'layout': go.Layout(
            title='PM2.5 Levels Over Time',
            xaxis=dict(title='Time'),
            yaxis=dict(title='PM2.5 (µg/m³)')
        )
    }
    return figure

if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=8050)
