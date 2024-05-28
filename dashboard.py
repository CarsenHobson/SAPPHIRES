import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import json
import os
from datetime import datetime

# Define the path to the directory containing the JSON files
json_dir = "/home/mainhubs/"

# Function to read the most recent data from each JSON file
def read_recent_data():
    recent_data = {}
    for file_name in os.listdir(json_dir):
        if file_name.endswith(".json"):
            file_path = os.path.join(json_dir, file_name)
            with open(file_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    try:
                        recent_entry = json.loads(lines[-1])  # Load the last line of the file
                        # Check if the timestamp is correctly processed
                        timestamp = datetime.fromtimestamp(recent_entry['timestamp']).strftime('%Y-%m-%d %I:%M %p')
                        recent_data[file_name] = {
                            'timestamp': timestamp,
                            'pm2.5': recent_entry.get('pm2.5', 'N/A'),
                            'humidity': recent_entry.get('humidity', 'N/A'),
                            'temperature': recent_entry.get('temperature', 'N/A'),
                            'wifi_strength': recent_entry.get('Wifi Strength', 'N/A')
                        }
                    except Exception as e:
                        print(f"Error processing file {file_name}: {e}")
    return recent_data

# Initialize the Dash app
app = dash.Dash(__name__)

# Define CSS styles
external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/litera/bootstrap.min.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Define the layout of the dashboard
app.layout = html.Div([
    html.Div([
        html.H1("Central Hub", className='display-4 text-center mb-4', style={'color': '#343a40'}),
        html.Div(id='live-update-text')
    ], className='jumbotron', style={'background-color': '#f8f9fa', 'border-radius': '15px', 'padding': '20px'}),
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # Update interval in milliseconds
        n_intervals=0
    )
], className='container-fluid', style={'background-color': '#e9ecef'})

# Define the callback to update the dashboard with recent data
@app.callback(
    Output('live-update-text', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_recent_data(n):
    recent_data = read_recent_data()
    if recent_data:
        data_display = []
        for file_name, data in recent_data.items():
            data_display.append(html.Div([
                html.H3(file_name, className='text-info mb-3'),
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Time", style={'background-color': '#343a40', 'color': 'white'}),
                        html.Th("PM2.5", style={'background-color': '#343a40', 'color': 'white'}),
                        html.Th("Humidity", style={'background-color': '#343a40', 'color': 'white'}),
                        html.Th("Temperature (F)", style={'background-color': '#343a40', 'color': 'white'}),
                        html.Th("Wifi Strength (%)", style={'background-color': '#343a40', 'color': 'white'})
                    ])),
                    html.Tbody(html.Tr([
                        html.Td(data['timestamp']),
                        html.Td(data['pm2.5']),
                        html.Td(data['humidity']),
                        html.Td(data['temperature']),
                        html.Td(data['wifi_strength'])
                    ]))
                ], className='table table-striped table-bordered')
            ]))
        return data_display
    else:
        return html.H3("No recent data available.", className='text-center mt-4')

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')


