import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import time
import csv
import RPi.GPIO as GPIO
import smbus
from qwic_i2c import QwiicSteadyStateRelay

# Initialize Dash app
app = dash.Dash(__name__)

# Define GPIO pin for PWM control
BLOWER_PWM_PIN = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(BLOWER_PWM_PIN, GPIO.OUT)

# Variables
button_pin = 18
csv_file = 'data_log.csv'
fieldnames = ['Timestamp', 'Pressure']
logging = False

# Set up PWM for blower control
blower_pwm = GPIO.PWM(BLOWER_PWM_PIN, 1000)  # PWM frequency = 1000 Hz
blower_pwm.start(0)  # Start PWM with duty cycle of 0%

# Set up SDP810 sensor
address = 0x25
bus = smbus.SMBus(1)
bus.write_i2c_block_data(address, 0x3F, [0xF9])
time.sleep(0.8)
bus.write_i2c_block_data(address, 0x36, [0x03])

# Set up Qwiic relays for damper control
damper_open_relay = QwiicSteadyStateRelay()
damper_open_relay.begin(3)  # Relay 3 for opening the damper

damper_close_relay = QwiicSteadyStateRelay()
damper_close_relay.begin(4)  # Relay 4 for closing the damper

# CSS styles
styles = {
    'textAlign': 'center',
    'marginBottom': '30px'
}

# Define app layout
app.layout = html.Div([
    html.H1("Differential Pressure Control Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Desired Pressure (Pa):", style={'fontSize': '20px', 'marginRight': '10px'}),
        dcc.Input(id='desired-pressure', type='number', value=1000, style={'fontSize': '20px', 'width': '150px'}),
        html.Div(id='output-container-button')
    ], style=styles),

    html.Div(id='current-pressure', style={'fontSize': '20px', 'marginTop': '20px'})
], style={'maxWidth': '600px', 'margin': 'auto', 'padding': '20px'})


# Define callback to control damper and blower
@app.callback(
    Output('output-container-button', 'children'),
    [Input('desired-pressure', 'value')]
)
def update_output(desired_pressure):
    global logging
    if logging:
        stop_logging()
    else:
        start_logging()

    while logging:
        time.sleep(0.5)
        reading = bus.read_i2c_block_data(address, 0, 9)
        pressure_value = reading[0] + float(reading[1]) / 255
        if pressure_value >= 0 and pressure_value < 128:
            differential_pressure = pressure_value * 240 / 256
        elif pressure_value > 128 and pressure_value <= 256:
            differential_pressure = -(256 - pressure_value) * 240 / 256
        elif pressure_value == 128:
            differential_pressure = 99999999

        # Calculate the difference between desired pressure and current pressure
        pressure_difference = desired_pressure - differential_pressure

        # Adjust blower speed based on pressure difference
        blower_speed = max(min(100 + pressure_difference, 100), 0)  # Ensure blower_speed stays within 0-100
        blower_pwm.ChangeDutyCycle(blower_speed)

        # Control damper position based on desired pressure


        # Open the damper (relay 3)
        damper_open_relay.set_relay_state(1)
        time.sleep(duration)

        # Close the damper (relay 4)
        damper_close_relay.set_relay_state(1)
        time.sleep(duration)

        return html.Div([
            html.H3(f"Desired Pressure Set to: {desired_pressure} Pa", style={'color': '#2ca02c', 'marginTop': '20px'})
        ])

# Function to control damper position based on desired pressure



# Callback to display current pressure
@app.callback(
    Output('current-pressure', 'children'),
    [Input('desired-pressure', 'value')]
)
def update_current_pressure(desired_pressure):
    reading = bus.read_i2c_block_data(address, 0, 9)
    pressure_value = reading[0] + float(reading[1]) / 255
    if pressure_value >= 0 and pressure_value < 128:
        differential_pressure = pressure_value * 240 / 256
    elif pressure_value > 128 and pressure_value <= 256:
        differential_pressure = -(256 - pressure_value) * 240 / 256
    elif pressure_value == 128:
        differential_pressure = 99999999

    return f"Current Pressure: {differential_pressure} Pa"


if __name__ == "__main__":
    app.run_server(debug=True)
