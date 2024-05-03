import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import RPi.GPIO as GPIO
from qwic_i2c import QwiicSteadyStateRelay

# Initialize Dash app
app = dash.Dash(__name__)

# Define GPIO pin for PWM control
BLOWER_PWM_PIN = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(BLOWER_PWM_PIN, GPIO.OUT)

# Variables
logging = False

# Set up PWM for blower control
blower_pwm = GPIO.PWM(BLOWER_PWM_PIN, 1000)  # PWM frequency = 1000 Hz
blower_pwm.start(0)  # Start PWM with duty cycle of 0%

# Set up Qwiic relay for damper control
damper_relay = QwiicSteadyStateRelay()
damper_relay.begin(3)  # Relay 3 for damper control

# Define colors
colors = {
    'background': '#f0f0f0',
    'text': '#333333'
}

# Define app layout
app.layout = html.Div(style={'backgroundColor': colors['background'], 'padding': '50px'}, children=[
    html.H1(children='Damper and Blower Control Dashboard', style={'textAlign': 'center', 'color': colors['text']}),

    html.Div(children=[
        html.Label("Blower Speed (%):", style={'fontSize': '20px', 'marginRight': '10px', 'color': colors['text']}),
        dcc.Input(id='blower-speed', type='number', value=50, min=0, max=100, style={'fontSize': '20px', 'width': '150px'}),
        html.Div(id='blower-output', style={'margin-top': '20px'})
    ], style={'marginBottom': '30px', 'textAlign': 'center'}),

    html.Div(children=[
        html.Button('Toggle Damper', id='toggle-damper', n_clicks=0, style={'fontSize': '16px', 'padding': '10px 20px'}),
        html.Div(id='damper-status', style={'margin-top': '20px'})
    ], style={'textAlign': 'center'})
])

# Callback to adjust blower speed
@app.callback(
    Output('blower-output', 'children'),
    [Input('blower-speed', 'value')]
)
def update_blower_speed(blower_speed):
    blower_pwm.ChangeDutyCycle(blower_speed)
    return html.Div([
        html.P(f"Blower Speed Set to: {blower_speed}%", style={'color': colors['text']})
    ])

# Callback for toggling damper
@app.callback(
    Output('damper-status', 'children'),
    [Input('toggle-damper', 'n_clicks')]
)
def toggle_damper(n_clicks):
    if n_clicks is not None and n_clicks % 2 == 1:  # Toggle on odd clicks
        damper_relay.set_relay_state(1)
        return html.P("Damper Opened", style={'color': colors['text']})
    else:  # Toggle on even clicks
        damper_relay.set_relay_state(0)
        return html.P("Damper Closed", style={'color': colors['text']})

if __name__ == "__main__":
    app.run_server(debug=True)
