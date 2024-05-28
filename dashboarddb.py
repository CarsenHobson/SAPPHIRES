# dashboard.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import sqlite3
from datetime import datetime

DATABASE_NAME = "mqtt_data.db"

def get_latest_values():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    latest_values = {}
    for table in ["ZeroW1", "ZeroW2", "ZeroW3", "ZeroW4"]:
        cursor.execute(f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            readable_timestamp = datetime.fromtimestamp(result[0]).strftime('%Y-%m-%d %H:%M:%S')
            latest_values[table] = {
                "timestamp": readable_timestamp,
                "key": result[1],
                "pm25": result[2],
                "temperature": result[3],
                "humidity": result[4],
                "wifi_strength": result[5],
            }
        else:
            latest_values[table] = {
                "timestamp": "No data",
                "key": None,
                "pm25": None,
                "temperature": None,
                "humidity": None,
                "wifi_strength": None,
            }
    conn.close()
    return latest_values

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/litera/bootstrap.min.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        html.H1("MQTT Sensor Dashboard", className='display-4 text-center mb-4', style={'color': '#343a40'}),
        html.Div(id='live-update-text')
    ], className='jumbotron', style={'background-color': '#f8f9fa', 'border-radius': '15px', 'padding': '20px'}),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # in milliseconds (refresh every minute)
        n_intervals=0
    )
], className='container-fluid', style={'background-color': '#e9ecef'})

@app.callback(
    Output('live-update-text', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    data = get_latest_values()
    if data:
        data_display = []
        for topic, values in data.items():
            data_display.append(html.Div([
                html.H3(topic, className='text-info mb-3'),
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Time", style={'background-color': '#343a40', 'color': 'white'}),
                        html.Th("PM2.5", style={'background-color': '#343a40', 'color': 'white'}),
                        html.Th("Humidity", style={'background-color': '#343a40', 'color': 'white'}),
                        html.Th("Temperature (F)", style={'background-color': '#343a40', 'color': 'white'}),
                        html.Th("Wifi Strength (%)", style={'background-color': '#343a40', 'color': 'white'})
                    ])),
                    html.Tbody(html.Tr([
                        html.Td(values['timestamp']),
                        html.Td(values['pm25']),
                        html.Td(values['humidity']),
                        html.Td(values['temperature']),
                        html.Td(values['wifi_strength'])
                    ]))
                ], className='table table-striped table-bordered')
            ]))
        return data_display
    else:
        return html.H3("No recent data available.", className='text-center mt-4')

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

