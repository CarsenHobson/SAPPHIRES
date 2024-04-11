import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import smbus
import time

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



# Define callback to update the current pressure and display it on the dashboard
@app.callback(
    Output('output-container-button', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_current_pressure(n_intervals):
    # Read current pressure from SDP810
    differential_pressure = read_sdp810(bus)
    
    if differential_pressure is not None:
        # Return the current pressure for display
        return f"Current Pressure: {differential_pressure} Pa"
    else:
        return "Error reading sensor data"

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
