import time
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from SDP810 import SDP810  # Assuming you have a library for SDP810
from qwic_i2c import QwiicSteadyStateRelay

# Initialize relays
damper_relay = QwiicSteadyStateRelay()
damper_relay.begin(17)  # Adjust pin as needed

blower_relay = QwiicSteadyStateRelay()
blower_relay.begin(18)  # Adjust pin as needed

# Set up SDP810 sensor
sdp = SDP810()

# Initialize Dash app
app = dash.Dash(__name__)

# Define app layout
app.layout = html.Div([
    html.H1("Differential Pressure Control Dashboard"),
    html.Label("Desired Pressure (Pa):"),
    dcc.Input(id='desired-pressure', type='number', value=1000),
    html.Button('Set Pressure', id='set-pressure-button', n_clicks=0),
    html.Div(id='output-container-button'),
    dcc.Interval(
        id='interval-component',
        interval=1000,  # in milliseconds
        n_intervals=0
    ),
])

# Define callback to update control signals and display current pressure
@app.callback(
    [Output('output-container-button', 'children'),
     Output('desired-pressure', 'disabled')],
    [Input('set-pressure-button', 'n_clicks')],
    [State('desired-pressure', 'value')]
)
def update_output(n_clicks, desired_pressure):
    if n_clicks > 0:
        # Enable/disable input
        disabled = True if n_clicks > 0 else False

        # Proportional control constants
        Kp_damper = 0.1  # Adjust as needed
        Kp_blower = 0.1  # Adjust as needed

        # Read pressure from SDP810
        current_pressure = sdp.read_pressure()

        # Calculate error
        error = desired_pressure - current_pressure

        # Calculate control signals
        damper_control = Kp_damper * error
        blower_control = Kp_blower * error

        # Limit control signals to within [0, 1] range
        damper_control = max(0, min(damper_control, 1))
        blower_control = max(0, min(blower_control, 1))

        # Apply control signals to relays
        damper_relay.set_relay_state(damper_control)
        blower_relay.set_relay_state(blower_control)

        # Return output
        output = f"Current Pressure: {current_pressure} Pa"
        return output, disabled
    else:
        return '', False

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
