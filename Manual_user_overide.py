import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import paho.mqtt.client as mqtt

MQTT_BROKER = "10.42.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = 'User Override'
MQTT_MESSAGE = "ON"

# MQTT Client Setup
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1("Manuel overide Dashboard"),
        html.Button(
            "Manual overide",
            id="manual-overide",
            style={
                "backgroundColor": "Green",
                "color": "white",
                "fontSize": "24px",
                "width": "200px",
                "height": "100px",
                "borderRadius": "10px",
                "display": "block",
                "margin": "auto",
            },
        ),
        html.Div(id="placeholder"),
    ],
    style={"textAlign": "center", "marginTop": "100px"},
)


@app.callback(
    Output("placeholder", "children"),
    [Input("manual-overide", "n_clicks")]
)
def emergency_shutoff(n_clicks):
    if n_clicks:
        client.publish(MQTT_TOPIC, MQTT_MESSAGE)
        return "Manual overide triggered"
    return ""


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=5000)

