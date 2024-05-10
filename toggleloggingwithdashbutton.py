import csv
from datetime import datetime
import time
from sps30 import SPS30
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Setup SPS30
sps = SPS30(1)
sps.start_measurement()

logging = False

def toggle_logging():
    global logging
    logging = not logging
    if logging:
        print("Logging started")
    else:
        print("Logging stopped")

def log_data():
    if logging:
        sps.read_measured_values()
        pm25 = sps.dict_values['pm2p5']
        if pm25 is not None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp}: PM2.5={pm25}")
            # Log data to CSV file
            with open('pm25_data.csv', mode='a') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, pm25])

# Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Button("Toggle Logging", id="toggle-button", n_clicks=0),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # in milliseconds
        n_intervals=0
    ),
])

@app.callback(
    Output('interval-component', 'disabled'),
    [Input('toggle-button', 'n_clicks')]
)
def update_logging_state(n_clicks):
    toggle_logging()
    return logging

@app.callback(
    Output('interval-component', 'interval'),
    [Input('toggle-button', 'n_clicks')]
)
def update_interval(n_clicks):
    return 1*1000 if logging else 1*10*1000  # Adjust the interval based on logging state

@app.callback(
    Output('interval-component', 'n_intervals'),
    [Input('toggle-button', 'n_clicks')]
)
def reset_interval(n_clicks):
    return 0

if __name__ == '__main__':
    app.run_server(debug=True)
