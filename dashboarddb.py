import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import sqlite3
from datetime import datetime
import time
import paho.mqtt.client as mqtt

DATABASE_NAME = "mqtt_data.db"
MQTT_BROKER = "mqtt.eclipseprojects.io"
MQTT_PORT = 1883

def on_publish(client, userdata, mid):
    try:
        userdata.remove(mid)
    except KeyError:
        print("on_publish() is called with a mid not present in unacked_publish")
        print("This is due to an unavoidable race-condition:")
        print("* publish() return the mid of the message sent.")
        print("* mid from publish() is added to unacked_publish by the main thread")
        print("* on_publish() is called by the loop_start thread")
        print("While unlikely (because on_publish() will be called after a network round-trip),")
        print(" this is a race-condition that COULD happen")
        print("")
        print("The best solution to avoid race-condition is using the msg_info from publish()")
        print("We could also try using a list of acknowledged mid rather than removing from pending list,")
        print("but remember that mid could be re-used !")

unacked_publish = set()
mqtt_client = mqtt.Client()
mqtt_client.on_publish = on_publish

mqtt_client.user_data_set(unacked_publish)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()

def send_mqtt_message(topic, message):
    msg_info = mqtt_client.publish(topic, message, qos=1)
    unacked_publish.add(msg_info.mid)
    msg_info.wait_for_publish()

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
        return ''
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id:
        send_mqtt_message("reset", "reboot")
    
    return ''

app.layout.children.append(html.Div(id='dummy-output', style={'display': 'none'}))

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

