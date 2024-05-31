import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import sqlite3
from datetime import datetime
import time
import paho.mqtt.client as mqtt
import logging

DATABASE_NAME = "mqtt_data.db"
MQTT_BROKER = "10.42.0.1"
MQTT_PORT = 1883
MQTT_USERNAME = "SAPPHIRE"
MQTT_PASSWORD = "SAPPHIRE"

def on_publish(client, userdata, result):
    pass
   


# Publish sensor data or error message
def publish_message(topic):
    try:
        client = mqtt.Client()
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        client.on_publish = on_publish
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(topic, "reboot", qos=1)
        logging.info(f"Sent reset")
    except Exception as e:
        error_message = f"Error publishing"
        logging.error(error_message)

def get_latest_values():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    latest_values = {}
    tables = ["ZeroW1", "ZeroW2", "ZeroW3", "ZeroW4"]

    for table in tables:
        try:
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
        except Exception as e:
            latest_values[table] = {
                "timestamp": f"Error: {str(e)}",
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
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    html.Div([
        html.H1("MQTT Sensor Dashboard", className='display-4 text-center mb-4', style={'color': '#343a40'}),
        html.Div(id='live-update-text')
    ], className='jumbotron', style={'background-color': '#f8f9fa', 'border-radius': '15px', 'padding': '20px'}),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # in milliseconds (refresh every minute)
        n_intervals=0
    ),
    html.Div(id='dummy-output', style={'display': 'none'})  # hidden div for callback output
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
                ], className='table table-striped table-bordered'),
                html.Button('Reboot', id=f'{topic}-button', n_clicks=0, className='btn btn-warning mt-2')
            ]))
        return data_display
    else:
        return html.H3("No recent data available.", className='text-center mt-4')

@app.callback(
    Output('dummy-output', 'children'),
    [Input(f'ZeroW{i+1}-button', 'n_clicks') for i in range(4)]
)
def handle_button_clicks(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        logging.debug("No button clicks detected")
        return ''
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    n_clicks = ctx.triggered[0]['value']
    if button_id and n_clicks > 0:
        logging.debug(f"Button {button_id} clicked {n_clicks} times")
        # Determine topic and message based on button_id
        topic_map = {
            'ZeroW1-button': 'Reset1',
            'ZeroW2-button': 'Reset2',
            'ZeroW3-button': 'Reset3',
            'ZeroW4-button': 'Reset4'
        }
        
        topic = topic_map.get(button_id, 'default/topic')
        
        publish_message(topic)
    
    return ''


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')


