import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Initialize Dash app
app = dash.Dash(__name__)

# Define colors
colors_dark = {
    'background': '#2c3e50',  # Dark background
    'text': '#ecf0f1',  # Light text
    'button_background': '#16a085',  # Darker green button background
    'button_text': '#FFFFFF',  # White button text
    'input_background': '#34495e',  # Dark input background
    'input_text': '#ecf0f1'  # Light input text
}

# Centralized styles
styles = {
    'container': {
        'padding': '20px',
        'backgroundColor': colors_dark['background'],
        'color': colors_dark['text'],
        'height': '100vh',
        'fontFamily': 'Arial, sans-serif',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'space-between'
    },
    'header': {
        'textAlign': 'center',
        'color': colors_dark['text'],
        'marginBottom': '10px',
        'fontSize': '48px',
        'fontFamily': 'Arial'
    },
    'subContainer': {
        'padding': '20px',
        'backgroundColor': colors_dark['background'],
        'color': colors_dark['text'],
        'borderRadius': '10px',
        'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
        'textAlign': 'center',
        'margin': '10px',
        'flex': '1'
    },
    'input': {
        'fontSize': '18px',
        'width': '150px',
        'backgroundColor': colors_dark['input_background'],
        'color': colors_dark['input_text'],
        'padding': '10px',
        'border': 'none',
        'borderRadius': '5px',
        'margin': '5px'
    },
    'label': {
        'fontSize': '24px',
        'marginRight': '10px',
        'color': colors_dark['text'],
        'fontFamily': 'Arial',
        'margin': '5px'
    },
    'output': {
        'marginTop': '10px',
        'textAlign': 'center',
        'color': colors_dark['text'],
        'fontFamily': 'Arial'
    },
    'button': {
        'fontSize': '18px',
        'backgroundColor': colors_dark['button_background'],
        'color': colors_dark['button_text'],
        'border': 'none',
        'borderRadius': '5px',
        'padding': '10px 20px',
        'cursor': 'pointer',
        'margin': '10px'
    }
}

# Define app layout
app.layout = html.Div([
    html.Div([
        html.Img(src="/assets/download2.png", style={'height': '100px', 'width': 'auto', 'float': 'left'}),
        html.Img(src="/assets/download3.png", style={'height': '100px', 'width': 'auto', 'float': 'right'}),
        html.H1(children='Benchtop Dashboard', style=styles['header']),
    ], style={'padding': '20px', 'backgroundColor': colors_dark['background'], 'color': colors_dark['text'],
              'height': '20%'}),

    html.Div([
        html.Div([
            html.Label("Blower Speed (%):", style=styles['label']),
            dcc.Input(id='blower-speed', type='number', value=50, min=0, max=100, style=styles['input']),
            html.Div(id='blower-output', style=styles['output']),
            dcc.Graph(id='blower-speed-gauge')
        ], style=styles['subContainer']),

        html.Div([
            html.Label("Damper Angle (°):", style=styles['label']),
            dcc.Input(id='damper-angle', type='number', value=0, min=0, max=90, step=1, style=styles['input']),
            html.Div(id='damper-status', style=styles['output']),
            dcc.Graph(id='damper-angle-gauge')
        ], style=styles['subContainer']),
    ], style={'display': 'flex', 'flexWrap': 'nowrap', 'justifyContent': 'space-around', 'alignItems': 'center',
              'height': '70%'}),

    html.Button('Startup Blower', id='startup-blower', n_clicks=0, style=styles['button']),
    html.Div(id='startup-blower-output', style=styles['output'])
], style=styles['container'])


# Callback to adjust blower speed
@app.callback(
    [Output('blower-output', 'children'),
     Output('blower-speed-gauge', 'figure')],
    [Input('blower-speed', 'value')]
)
def update_blower_speed(blower_speed):
    gauge_chart = go.Figure(go.Indicator(
        mode="gauge+number",
        value=blower_speed,
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': colors_dark['button_background']}},
        title={'text': "Blower Speed"}
    ))
    gauge_chart.update_layout(
        paper_bgcolor=colors_dark['background'],
        font=dict(color=colors_dark['text'])
    )

    return html.Div([
        html.P(f"Blower Speed Set to: {blower_speed}%", style={'fontSize': '24px', 'fontFamily': 'Arial'})
    ]), gauge_chart


# Callback for setting damper angle
@app.callback(
    [Output('damper-status', 'children'),
     Output('damper-angle-gauge', 'figure')],
    [Input('damper-angle', 'value')]
)
def set_damper_angle(damper_angle):
    gauge_chart = go.Figure(go.Indicator(
        mode="gauge+number",
        value=damper_angle,
        gauge={'axis': {'range': [0, 90]},
               'bar': {'color': colors_dark['button_background']}},
        title={'text': "Damper Angle"}
    ))
    gauge_chart.update_layout(
        paper_bgcolor=colors_dark['background'],
        font=dict(color=colors_dark['text'])
    )

    return html.P(f"Damper Angle Set to: {damper_angle}°",
                  style={'fontSize': '24px', 'fontFamily': 'Arial'}), gauge_chart


# Callback for Startup Blower button
@app.callback(
    Output('startup-blower-output', 'children'),
    [Input('startup-blower', 'n_clicks')]
)
def startup_blower(n_clicks):
    if n_clicks > 0:
        return html.P(f"Blower started ", style={'fontSize': '24px', 'fontFamily': 'Arial'})
    return ""

if __name__ == "__main__":
    app.run_server(debug=True)
