import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Initialize Dash app
app = dash.Dash(__name__)

# Define colors
colors_dark = {
    'background': '#808080',   # Dark background
    'text': '#f5f5f5',         # Light text
    'button_background': '#007F00',  # Darker green button background
    'button_text': '#FFFFFF',  # White button text
    'input_background': '#333333',   # Dark input background
    'input_text': '#FFFFFF'    # Light input text
}

# Define app layout
app.layout = html.Div([
    html.Div([
        html.Img(src="/assets/download2.png", style={'height': '150px', 'width': 'auto', 'float': 'left'}),
        html.Img(src="/assets/download3.png", style={'height': '150px', 'width': 'auto', 'float': 'right'}),
        html.H1(children='Benchtop Dashboard', style={'textAlign': 'center', 'color': '#f5f5f5', 'marginBottom': '10px', 'fontSize': '48px', 'fontFamily': 'Arial'}),
    ], style={'padding': '40px', 'backgroundColor': colors_dark['background'], 'color': colors_dark['text'], 'height': '30%'}),
    html.Div([
        html.Div([
            dcc.Input(id='blower-speed', type='number', value=50, min=0, max=100, style={'fontSize': '18px', 'width': '150px', 'backgroundColor': colors_dark['input_background'], 'color': colors_dark['input_text']}),
            html.Label("Blower Speed (%):", style={'fontSize': '24px', 'marginRight': '10px', 'color': colors_dark['text'], 'fontFamily': 'Arial'}),
            html.Div(id='blower-output', style={'marginTop': '10px', 'textAlign': 'center', 'color': colors_dark['text'], 'fontFamily': 'Arial'}),
        ], style={'marginBottom': '20px', 'textAlign': 'center'}),
        html.Div([
            html.Button('Toggle Damper', id='toggle-damper', n_clicks=0, style={'fontSize': '18px', 'padding': '10px 20px', 'backgroundColor': colors_dark['button_background'], 'color': colors_dark['button_text'], 'borderRadius': '5px', 'cursor': 'pointer', 'fontFamily': 'Arial'}),
            html.Div(id='damper-status', style={'marginTop': '10px', 'textAlign': 'center', 'color': colors_dark['text'], 'fontFamily': 'Arial'}),
        ], style={'textAlign': 'center'}),
    ], style={'padding': '20px', 'backgroundColor': colors_dark['background'], 'color': colors_dark['text'], 'borderRadius': '10px', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)', 'height': '80%'}),
], style={'fontFamily': 'Arial, sans-serif', 'height': '100vh'})

# Callback to adjust blower speed
@app.callback(
    Output('blower-output', 'children'),
    [Input('blower-speed', 'value')]
)
def update_blower_speed(blower_speed):
    return html.Div([
        html.P(f"Blower Speed Set to: {blower_speed}%", style={'fontSize': '24px', 'fontFamily': 'Arial'})
    ])

# Callback for toggling damper
@app.callback(
    Output('damper-status', 'children'),
    [Input('toggle-damper', 'n_clicks')]
)
def toggle_damper(n_clicks):
    if n_clicks is not None and n_clicks % 2 == 1:  # Toggle on odd clicks
        return html.P("Damper Opened", style={'fontSize': '24px', 'fontFamily': 'Arial'})
    else:  # Toggle on even clicks
        return html.P("Damper Closed", style={'fontSize': '24px', 'fontFamily': 'Arial'})

if __name__ == "__main__":
    app.run_server(debug=True)
