import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import time
import qwiic_relay
import pigpio
import time
# Constants
PWM_PIN = 12  # GPIO pin for PWM signal (BCM numbering)
PWM_FREQUENCY = 1000  # Frequency for PWM signal in Hz
MIN_DUTY_CYCLE = 50  # Minimum duty cycle (50%)
MAX_DUTY_CYCLE = 100  # Maximum duty cycle (100%)
# Initialize Qwiic relay
myRelays = qwiic_relay.QwiicRelay()

# Initialize pigpio
pi = pigpio.pi()

# Initialize Dash app
app = dash.Dash(__name__)

# Define colors
colors = {
    'background': '#808080',   # Dark background
    'text': '#f5f5f5',         # Light text
    'button_background': '#007F00',  # Darker green button background
    'button_text': '#FFFFFF',  # White button text
    'input_background': '#333333',   # Dark input background
    'input_text': '#FFFFFF'    # Light input text
}

# Initialize Qwiic relay
myRelays = qwiic_relay.QwiicRelay()

# Define app layout
app.layout = html.Div([
    html.Div([
        html.Img(src="/assets/download2.png", style={'height': '150px', 'width': 'auto', 'float': 'left'}),
        html.Img(src="/assets/download3.png", style={'height': '150px', 'width': 'auto', 'float': 'right'}),
        html.H1(children='Benchtop Dashboard', style={'textAlign': 'center', 'color': colors['text'], 'marginBottom': '10px', 'fontSize': '48px', 'fontFamily': 'Arial'}),
    ], style={'padding': '40px', 'backgroundColor': colors['background'], 'color': colors['text'], 'height': '30%'}),
    html.Div([
        html.Div([
            dcc.Input(id='blower-speed', type='number', value=50, min=0, max=100, style={'fontSize': '18px', 'width': '150px', 'backgroundColor': colors['input_background'], 'color': colors['input_text']}),
            html.Label("Blower Speed (%):", style={'fontSize': '24px', 'marginRight': '10px', 'color': colors['text'], 'fontFamily': 'Arial'}),
            html.Div(id='blower-output', style={'marginTop': '10px', 'textAlign': 'center', 'color': colors['text'], 'fontFamily': 'Arial'}),
        ], style={'marginBottom': '20px', 'textAlign': 'center'}),
        html.Div([
            dcc.Input(id='damper-angle', type='number', value=0, min=0, max=90, step=1, style={'fontSize': '18px', 'width': '150px', 'backgroundColor': colors['input_background'], 'color': colors['input_text']}),
            html.Label("Damper Angle (°):", style={'fontSize': '24px', 'marginRight': '10px', 'color': colors['text'], 'fontFamily': 'Arial'}),
            html.Div(id='damper-status', style={'marginTop': '10px', 'textAlign': 'center', 'color': colors['text'], 'fontFamily': 'Arial'}),
        ], style={'textAlign': 'center'}),
    ], style={'padding': '20px', 'backgroundColor': colors['background'], 'color': colors['text'], 'borderRadius': '10px', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)', 'height': '80%'}),
], style={'fontFamily': 'Arial, sans-serif', 'height': '100vh'})

# Callback to adjust blower speed
@app.callback(
    Output('blower-output', 'children'),
    [Input('blower-speed', 'value')]
)
def update_blower_speed(blower_speed):
    pi.set_PWM_dutycycle(PWM_PIN, blower_speed * 0.01 * 255)
    return html.Div([
        html.P(f"Blower Speed Set to: {blower_speed}%", style={'fontSize': '24px', 'fontFamily': 'Arial'})
    ])

# Callback for setting damper angle
@app.callback(
    Output('damper-status', 'children'),
    [Input('damper-angle', 'value')]
)
def set_damper_angle(damper_angle):
    # Calculate the time required to move the damper to the desired angle
    time_to_move = (damper_angle / 90) * 53  # Total time for 0-90° is 53 seconds
    myRelays.set_relay_on(1)  # Start moving the damper
    time.sleep(time_to_move)
    myRelays.set_relay_off(1)  # Stop moving the damper
    return html.P(f"Damper Angle Set to: {damper_angle}°", style={'fontSize': '24px', 'fontFamily': 'Arial'})

def startup_blower(n_clicks):
    if n_clicks > 0:
        pi.set_PWM_dutycycle(PWM_PIN, MAX_DUTY_CYCLE * 2.55)
        return html.P(f"Blower started ", style={'fontSize': '24px', 'fontFamily': 'Arial'})
        time.sleep(1)
        pi.set_PWM_dutycycle(PWM_PIN, 0)
    return ""


if __name__ == "__main__":
    app.run_server(debug=True)
