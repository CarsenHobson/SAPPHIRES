import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import sqlite3
import pandas as pd
from dash.dependencies import Input, Output

DATABASE_NAME = "mqtt_data.db"

def get_latest_values():
    """Fetch the latest values from each table."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    latest_values = {}
    for table in ["ZeroW1", "ZeroW2", "ZeroW3", "ZeroW4"]:
        cursor.execute(f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            latest_values[table] = {
                "timestamp": result[0],
                "key": result[1],
                "pm25": result[2],
                "temperature": result[3],
                "humidity": result[4],
                "wifi_strength": result[5],
            }

    conn.close()
    return latest_values

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("MQTT Sensor Dashboard", className="text-center my-4"))),
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("ZeroW1"),
            dbc.CardBody([
                html.P(id="ZeroW1-pm25"),
                html.P(id="ZeroW1-temperature"),
                html.P(id="ZeroW1-humidity"),
                html.P(id="ZeroW1-wifi_strength")
            ])
        ]), width=3),
        dbc.Col(dbc.Card([
            dbc.CardHeader("ZeroW2"),
            dbc.CardBody([
                html.P(id="ZeroW2-pm25"),
                html.P(id="ZeroW2-temperature"),
                html.P(id="ZeroW2-humidity"),
                html.P(id="ZeroW2-wifi_strength")
            ])
        ]), width=3),
        dbc.Col(dbc.Card([
            dbc.CardHeader("ZeroW3"),
            dbc.CardBody([
                html.P(id="ZeroW3-pm25"),
                html.P(id="ZeroW3-temperature"),
                html.P(id="ZeroW3-humidity"),
                html.P(id="ZeroW3-wifi_strength")
            ])
        ]), width=3),
        dbc.Col(dbc.Card([
            dbc.CardHeader("ZeroW4"),
            dbc.CardBody([
                html.P(id="ZeroW4-pm25"),
                html.P(id="ZeroW4-temperature"),
                html.P(id="ZeroW4-humidity"),
                html.P(id="ZeroW4-wifi_strength")
            ])
        ]), width=3)
    ]),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # in milliseconds (refresh every minute)
        n_intervals=0
    )
])

@app.callback(
    [Output("ZeroW1-pm25", "children"),
     Output("ZeroW1-temperature", "children"),
     Output("ZeroW1-humidity", "children"),
     Output("ZeroW1-wifi_strength", "children"),
     Output("ZeroW2-pm25", "children"),
     Output("ZeroW2-temperature", "children"),
     Output("ZeroW2-humidity", "children"),
     Output("ZeroW2-wifi_strength", "children"),
     Output("ZeroW3-pm25", "children"),
     Output("ZeroW3-temperature", "children"),
     Output("ZeroW3-humidity", "children"),
     Output("ZeroW3-wifi_strength", "children"),
     Output("ZeroW4-pm25", "children"),
     Output("ZeroW4-temperature", "children"),
     Output("ZeroW4-humidity", "children"),
     Output("ZeroW4-wifi_strength", "children")],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    data = get_latest_values()
    return (
        f"PM2.5: {data['ZeroW1']['pm25']}",
        f"Temperature: {data['ZeroW1']['temperature']} °F",
        f"Humidity: {data['ZeroW1']['humidity']} %",
        f"Wifi Strength: {data['ZeroW1']['wifi_strength']}",
        f"PM2.5: {data['ZeroW2']['pm25']}",
        f"Temperature: {data['ZeroW2']['temperature']} °F",
        f"Humidity: {data['ZeroW2']['humidity']} %",
        f"Wifi Strength: {data['ZeroW2']['wifi_strength']}",
        f"PM2.5: {data['ZeroW3']['pm25']}",
        f"Temperature: {data['ZeroW3']['temperature']} °F",
        f"Humidity: {data['ZeroW3']['humidity']} %",
        f"Wifi Strength: {data['ZeroW3']['wifi_strength']}",
        f"PM2.5: {data['ZeroW4']['pm25']}",
        f"Temperature: {data['ZeroW4']['temperature']} °F",
        f"Humidity: {data['ZeroW4']['humidity']} %",
        f"Wifi Strength: {data['ZeroW4']['wifi_strength']}"
    )

if __name__ == '__main__':
    app.run_server(debug=True)
