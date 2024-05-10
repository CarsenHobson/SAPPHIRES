import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import smbus
import time
import qwiic_relay

# Initialize Dash app
app = dash.Dash(__name__)

# Initialize Qwiic relay
myRelays = qwiic_relay.QwiicRelay()

# Define colors
colors = {
    'background': '#f0f0f0',
    'text': '#333333',
    'button': '#1f77b4'
}

# Define app layout
app.layout = html.Div(style={'backgroundColor': colors['background'], 'padding': '50px'}, children=[
    html.H1("Differential Pressure Control Dashboard", style={'textAlign': 'center', 'color': colors['text']}),

    html.Label("Desired Pressure (Pa):"),
    dcc.Input(id='desired-pressure', type='number', value=1000),
    html.Button('Set Pressure', id='set-pressure-button', n_clicks=0),
    html.Div(id='output-container-button'),

    html.Div(children=[
        html.Label("Blower Speed (%):", style={'fontSize': '20px', 'marginRight': '10px', 'color': colors['text']}),
        dcc.Input(id='blower-speed', type='number', value=50, min=0, max=100, style={'fontSize': '20px', 'width': '150px'}),
        html.Div(id='blower-output', style={'margin-top': '20px'})
    ], style={'marginBottom': '30px', 'textAlign': 'center'}),

    html.Div(children=[
        html.Button('Toggle Damper', id='toggle-damper', n_clicks=0, style={'fontSize': '16px', 'padding': '10px 20px', 'backgroundColor': colors['button'], 'color': 'white', 'border': 'none'}),
        html.Div(id='damper-status', style={'margin-top': '20px'})
    ], style={'textAlign': 'center'})
])

bus = smbus.SMBus(1)
address = 0x25
bus.write_i2c_block_data(address, 0x3F, [0xF9])
time.sleep(0.8)

bus.write_i2c_block_data(address, 0x36, [0x03])

def read_sdp810(bus):
    """Read data from the SDP810 sensor and return the differential pressure."""
    try:
        # Read data from the sensor
        reading = bus.read_i2c_block_data(address, 0, 9)
        pressure_value = reading[0] + float(reading[1]) / 255
        
        # Calculate differential pressure
        if 0 <= pressure_value < 128:
            differential_pressure = pressure_value * 240 / 256
        elif 128 < pressure_value <= 256:
            differential_pressure = -(256 - pressure_value) * 240 / 256
        elif pressure_value == 128:
            differential_pressure = float('inf')  # Invalid reading indicator

        return differential_pressure
    except Exception as e:
        print(f"Error reading sensor data: {e}")
        return None

# Callback to adjust blower speed and toggle damper
@app.callback(
    [Output('blower-output', 'children'), Output('damper-status', 'children')],
    [Input('blower-speed', 'value'), Input('toggle-damper', 'n_clicks')],
    [State('desired-pressure', 'value')]
)
def update_blower_and_damper(blower_speed, n_clicks, desired_pressure):
    try:
        if n_clicks is not None and n_clicks > 0:  # Toggle on odd clicks
            myRelays.set_relay_on(1)
            time.sleep(0.5)
            myRelays.set_relay_off(1)
            damper_status = "Damper Toggled"
        else:
            myRelays.set_relay_off(1)
            damper_status = ""

        differential_pressure = read_sdp810(bus)
        if differential_pressure is not None:
            if differential_pressure < desired_pressure:
                myRelays.set_slow_pwm(2, blower_speed*0.01*120)
                blower_output = f"Blower Speed Set to: {blower_speed}%"
            else:
                myRelays.set_slow_pwm(2, 0)  # Stop blower
                blower_output = "Pressure reached desired level, blower stopped."
        else:
            blower_output = "Error reading sensor data"
        
        return html.Div([
            html.P(blower_output, style={'color': colors['text']})
        ]), html.Div([
            html.P(damper_status, style={'color': colors['text']})
        ])
    except Exception as e:
        print(f"Error: {e}")
        return html.Div([
            html.P("Error occurred.", style={'color': colors['text']})
        ])

# Define callback to update the current pressure and display it on the dashboard
@app.callback(
    Output('output-container-button', 'children'),
    [Input('blower-speed', 'value'), Input('toggle-damper', 'n_clicks')]
)
def update_current_pressure(blower_speed, n_clicks):
    try:
        differential_pressure = read_sdp810(bus)
        if differential_pressure is not None:
            return f"Current Pressure: {differential_pressure} Pa"
        else:
            return "Error reading sensor data"
    except Exception as e:
        print(f"Error: {e}")
        return "Error occurred."

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

