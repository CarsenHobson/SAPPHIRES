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
    )
])

@app.callback(
    Output('dashboard', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    data = get_latest_values()
    cards = []
    for topic, values in data.items():
        card = html.Div([
            html.H3(topic, style={'textAlign': 'center'}),
            html.P(f"PM2.5: {values['pm25']}", style={'textAlign': 'center'}),
            html.P(f"Temperature: {values['temperature']} °F", style={'textAlign': 'center'}),
            html.P(f"Humidity: {values['humidity']} %", style={'textAlign': 'center'}),
            html.P(f"Wifi Strength: {values['wifi_strength']}", style={'textAlign': 'center'})
        ], style={
            'border': '1px solid #ccc',
            'padding': '10px',
            'borderRadius': '10px',
            'width': '200px',
            'margin': '10px'
        })
        cards.append(card)
    return cards

if __name__ == '__main__':
    app.run_server(debug=True)
