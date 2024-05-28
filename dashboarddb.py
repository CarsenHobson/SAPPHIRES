import dash
from dash import html, dcc
import sqlite3
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
        else:
            latest_values[table] = {
                "timestamp": None,
                "key": None,
                "pm25": None,
                "temperature": None,
                "humidity": None,
                "wifi_strength": None,
            }

    conn.close()
    return latest_values

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("MQTT Sensor Dashboard", style={'textAlign': 'center', 'marginBottom': '30px'}),
    html.Div(id='dashboard', style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap'}),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # in milliseconds (refresh every minute)
        n_intervals=0
    ),
    html.Footer("MQTT Dashboard © 2024", style={'textAlign': 'center', 'padding': '20px', 'background': '#f1f1f1', 'marginTop': '30px'})
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f9f9f9', 'padding': '20px'})

@app.callback(
    Output('dashboard', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    data = get_latest_values()
    cards = []
    for topic, values in data.items():
        card = html.Div([
            html.H3(topic, style={'textAlign': 'center', 'backgroundColor': '#007BFF', 'color': 'white', 'padding': '10px', 'borderRadius': '5px 5px 0 0'}),
            html.Div([
                html.P(f"Timestamp: {values['timestamp']}", style={'textAlign': 'center'}),
                html.P(f"PM2.5: {values['pm25']}", style={'textAlign': 'center'}),
                html.P(f"Temperature: {values['temperature']} °F", style={'textAlign': 'center'}),
                html.P(f"Humidity: {values['humidity']} %", style={'textAlign': 'center'}),
                html.P(f"Wifi Strength: {values['wifi_strength']}", style={'textAlign': 'center'})
            ], style={'padding': '10px'})
        ], style={
            'border': '1px solid #ccc',
            'borderRadius': '10px',
            'width': '200px',
            'margin': '10px',
            'boxShadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)',
            'transition': '0.3s',
            'backgroundColor': 'white'
        })
        cards.append(card)
    return cards

if __name__ == '__main__':
    app.run_server(debug=True)


