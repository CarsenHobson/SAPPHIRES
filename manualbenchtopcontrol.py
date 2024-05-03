import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import time
import qwiic_relay

# Initialize Dash app
app = dash.Dash(__name__)

# Variables
logging = False

# Initialize Qwiic relay
DamperRelay = qwiic_relay.QwiicRelay()

# Define colors
colors = {
    'background': '#f0f0f0',
    'text': '#333333',
    'button': '#1f77b4'
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
        html.Button('Toggle Damper', id='toggle-damper', n_clicks=0, style={'fontSize': '16px', 'padding': '10px 20px', 'backgroundColor': colors['button'], 'color': 'white', 'border': 'none'}),
        html.Div(id='damper-status', style={'margin-top': '20px'})
    ], style={'textAlign': 'center'})
])

# Callback to adjust blower speed
@app.callback(
    Output('blower-output', 'children'),
    [Input('blower-speed', 'value')]
)
def update_blower_speed(blower_speed):
    myRelays.set_slow_pwm(2, blower_speed*0.01*120)
    return html.Div([
        html.P(f"Blower Speed Set to: {blower_speed}%", style={'color': colors['text']})
    ])

# Callback for toggling damper
@app.callback(
    Output('damper-status', 'children'),
    [Input('toggle-damper', 'n_clicks')]
)
def toggle_damper(n_clicks):
    if n_clicks is not None and n_clicks > 0:  # Toggle on odd clicks
        myRelays.set_relay_on(1)
        time.sleep(0.5)
        myRelays.set_relay_off(1)
        return html.P("Damper Toggled", style={'color': colors['text']})
    else:
        myRelays.set_relay_off(1)

if __name__ == "__main__":
    app.run_server(debug=True)
