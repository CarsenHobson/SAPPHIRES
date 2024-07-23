import dash
from dash import dcc, html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import os

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Define the CSV file path
csv_file_path = 'survey_results.csv'

# Check if the CSV file exists, and if not, create it with the correct headers
if not os.path.isfile(csv_file_path):
    df = pd.DataFrame(columns=['Timestamp', 'Satisfaction', 'Comments'])
    df.to_csv(csv_file_path, index=False)

# Function to create keyboard layout
def create_keyboard():
    rows = [
        list("1234567890"),
        list("QWERTYUIOP"),
        list("ASDFGHJKL"),
        list("ZXCVBNM")
    ]
    keyboard_layout = []
    for row in rows:
        keyboard_layout.append(html.Div([dbc.Button(char, id={'type': 'key', 'index': char}, n_clicks=0) for char in row], className="mb-1"))
    keyboard_layout.append(html.Div([
        dbc.Button("Space", id={'type': 'key', 'index': ' '}, n_clicks=0, style={'width': '60px'}),
        dbc.Button("Backspace", id={'type': 'key', 'index': 'Backspace'}, n_clicks=0)
    ]))
    return keyboard_layout

# Layout of the app
app.layout = html.Div([
    dcc.Interval(id='interval-component', interval=600*1000, n_intervals=0),  # 10 minutes interval
    dcc.Store(id='show-survey', data=True),
    dcc.Store(id='reset-form', data=False),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Survey")),
            dbc.ModalBody([
                html.Div([
                    html.Label("How satisfied are you with the dashboard?"),
                    dcc.RadioItems(
                        id='satisfaction',
                        options=[
                            {'label': 'Very Satisfied', 'value': '5'},
                            {'label': 'Satisfied', 'value': '4'},
                            {'label': 'Neutral', 'value': '3'},
                            {'label': 'Dissatisfied', 'value': '2'},
                            {'label': 'Very Dissatisfied', 'value': '1'},
                        ],
                        style={'margin': '20px 0'},
                    ),
                    html.Br(),
                    html.Label("Additional Comments:"),
                    dcc.Textarea(id='comments', style={'width': '100%', 'height': '150px', 'resize': 'none'}),
                    html.Div(id='error-message', style={'color': 'red', 'marginTop': '10px'}),
                    html.Div(create_keyboard(), id='keyboard')
                ], style={'fontSize': '18px'}),
            ]),
            dbc.ModalFooter(
                dbc.Button("Submit", id="submit-survey", className="ms-auto", n_clicks=0, style={'fontSize': '18px'})
            ),
        ],
        id="modal",
        is_open=False,
        size="lg",  # Make the modal large
        backdrop="static",  # Prevents closing by clicking outside
        keyboard=False,  # Prevents closing by pressing escape key
    ),
    html.Div(id='dashboard-content', children=[
        html.H3('Welcome to the Dashboard'),
        html.Hr(),
        # Here you can add the initial dashboard content
        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3, 4], 'y': [4, 1, 3, 5], 'type': 'bar', 'name': 'Example Data'},
                ],
                'layout': {
                    'title': 'Example Graph'
                }
            }
        ),
        dcc.Dropdown(
            id='example-dropdown',
            options=[
                {'label': 'Option 1', 'value': '1'},
                {'label': 'Option 2', 'value': '2'},
                {'label': 'Option 3', 'value': '3'},
            ],
            value='1'
        ),
        dcc.Input(id='example-input', value='Type something here...', type='text'),
        html.Div(id='example-output')
    ]),
])

@app.callback(
    Output('comments', 'value'),
    [Input({'type': 'key', 'index': ALL}, 'n_clicks')],
    State('comments', 'value')
)
def update_textarea(n_clicks, current_text):
    triggered = ctx.triggered_id
    if triggered and triggered['type'] == 'key':
        key = triggered['index']
        if key == 'Backspace':
            current_text = current_text[:-1]
        else:
            current_text += key
    return current_text

@app.callback(
    Output('modal', 'is_open'),
    Output('show-survey', 'data'),
    Output('error-message', 'children'),
    Output('satisfaction', 'value'),
    Output('comments', 'value'),
    Input('interval-component', 'n_intervals'),
    Input('submit-survey', 'n_clicks'),
    State('satisfaction', 'value'),
    State('comments', 'value'),
    State('show-survey', 'data'),
    State('modal', 'is_open'),
)
def toggle_modal(n_intervals, n_clicks, satisfaction, comments, show_survey, is_open):
    trigger = ctx.triggered_id
    
    if trigger == 'interval-component':
        return True, False, '', None, ''  # Show survey, reset flag and form fields, clear error message

    if trigger == 'submit-survey':
        if satisfaction:
            # Save the survey results to the CSV file
            new_data = pd.DataFrame({
                'Timestamp': [pd.Timestamp.now()],
                'Satisfaction': [satisfaction],
                'Comments': [comments]
            })
            new_data.to_csv(csv_file_path, mode='a', header=False, index=False)
            return False, True, '', None, ''  # Close survey, set flag, clear error message and form fields
        else:
            return True, False, 'Please answer all required questions.', satisfaction, comments  # Show error message

    return is_open, show_survey, '', satisfaction, comments

@app.callback(
    Output('dashboard-content', 'children'),
    Input('submit-survey', 'n_clicks'),
    State('satisfaction', 'value'),
    State('comments', 'value'),
)
def update_dashboard(n_clicks, satisfaction, comments):
    if n_clicks > 0 and satisfaction:
        # Here you can process the survey results
        print(f"Satisfaction: {satisfaction}, Comments: {comments}")
        # Return to the original dashboard state
        return html.Div([
            html.H3('Welcome to the Dashboard'),
            html.Hr(),
            # Here you can add the initial dashboard content
            dcc.Graph(
                id='example-graph',
                figure={
                    'data': [
                        {'x': [1, 2, 3, 4], 'y': [4, 1, 3, 5], 'type': 'bar', 'name': 'Example Data'},
                    ],
                    'layout': {
                        'title': 'Example Graph'
                    }
                }
            ),
            dcc.Dropdown(
                id='example-dropdown',
                options=[
                    {'label': 'Option 1', 'value': '1'},
                    {'label': 'Option 2', 'value': '2'},
                    {'label': 'Option 3', 'value': '3'},
                ],
                value='1'
            ),
            dcc.Input(id='example-input', value='Type something here...', type='text'),
            html.Div(id='example-output')
        ])
    else:
        return html.Div([
            html.H3('Welcome to the Dashboard'),
            html.Hr(),
            # Here you can add the initial dashboard content
            dcc.Graph(
                id='example-graph',
                figure={
                    'data': [
                        {'x': [1, 2, 3, 4], 'y': [4, 1, 3, 5], 'type': 'bar', 'name': 'Example Data'},
                    ],
                    'layout': {
                        'title': 'Example Graph'
                    }
                }
            ),
            dcc.Dropdown(
                id='example-dropdown',
                options=[
                    {'label': 'Option 1', 'value': '1'},
                    {'label': 'Option 2', 'value': '2'},
                    {'label': 'Option 3', 'value': '3'},
                ],
                value='1'
            ),
            dcc.Input(id='example-input', value='Type something here...', type='text'),
            html.Div(id='example-output')
        ])

if __name__ == '__main__':
    app.run_server(debug=True)

