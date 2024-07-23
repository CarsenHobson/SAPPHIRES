import dash
from dash import dcc, html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import os

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
server = app.server

# Define the CSV file path
csv_file_path = 'survey_results.csv'

# Check if the CSV file exists, and if not, create it with the correct headers
if not os.path.isfile(csv_file_path):
    df = pd.DataFrame(columns=['Timestamp', 'Satisfaction', 'Comments'])
    df.to_csv(csv_file_path, index=False)


# Function to create keyboard layout
def create_keyboard(shift=False):
    rows = [
        list("1234567890"),
        list("QWERTYUIOP" if shift else "qwertyuiop"),
        list("ASDFGHJKL" if shift else "asdfghjkl"),
        list("ZXCVBNM" if shift else "zxcvbnm")
    ]
    button_style = {'margin': '8px', 'width': '80px', 'height': '80px', 'fontSize': '32px'}
    space_button_style = {'margin': '8px', 'width': '600px', 'height': '80px', 'fontSize': '32px'}
    shift_back_style = {'margin': '8px', 'width': '100px', 'height': '80px', 'fontSize': '32px'}
    keyboard_layout = []
    for row in rows:
        keyboard_layout.append(
            html.Div(
                [dbc.Button(char, id={'type': 'key', 'index': char}, n_clicks=0, style=button_style) for char in row],
                className="d-flex justify-content-center mb-2"
            )
        )
    keyboard_layout.append(
        html.Div(
            [
                dbc.Button("Shift", id='shift-key', n_clicks=0, style=shift_back_style),
                dbc.Button("Space", id={'type': 'key', 'index': ' '}, n_clicks=0, style=space_button_style),
                dbc.Button("Back", id={'type': 'key', 'index': 'Backspace'}, n_clicks=0, style=shift_back_style)
            ],
            className="d-flex justify-content-center"
        )
    )
    return keyboard_layout


# Layout of the app
app.layout = html.Div([
    dcc.Interval(id='interval-component', interval=10 * 1000, n_intervals=0),  # 10 minutes interval
    dcc.Store(id='show-survey', data=True),
    dcc.Store(id='reset-form', data=False),
    dcc.Store(id='shift-state', data=False),  # Store to keep track of shift state
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Survey"), style={'fontSize': '32px'}),
            dbc.ModalBody([
                html.Div([
                    html.Label("How satisfied are you with the dashboard?", style={'fontSize': '24px'}),
                    dcc.RadioItems(
                        id='satisfaction',
                        options=[
                            {'label': 'Very Satisfied', 'value': '5'},
                            {'label': 'Satisfied', 'value': '4'},
                            {'label': 'Neutral', 'value': '3'},
                            {'label': 'Dissatisfied', 'value': '2'},
                            {'label': 'Very Dissatisfied', 'value': '1'},
                        ],
                        style={'margin': '20px 0', 'fontSize': '24px'},
                    ),
                    html.Br(),
                    html.Label("Additional Comments:", style={'fontSize': '24px'}),
                    dcc.Textarea(id='comments',
                                 style={'width': '100%', 'height': '200px', 'resize': 'none', 'fontSize': '24px'}),
                    html.Div(id='error-message', style={'color': 'red', 'marginTop': '10px', 'fontSize': '24px'}),
                    html.Div(id='keyboard-container', children=create_keyboard())
                ], style={'fontSize': '24px'}),
            ]),
            dbc.ModalFooter(
                dbc.Button("Submit", id="submit-survey", className="ms-auto", n_clicks=0, style={'fontSize': '24px'})
            ),
        ],
        id="modal",
        is_open=False,
        size="xl",  # Make the modal extra large
        backdrop="static",  # Prevents closing by clicking outside
        keyboard=False,  # Prevents closing by pressing escape key
    ),
    html.Div(id='dashboard-content', children=[
        html.H3('Welcome to the Dashboard', style={'fontSize': '32px'}),
        html.Hr(),
        # Here you can add the initial dashboard content
    ]),
])


@app.callback(
    Output('keyboard-container', 'children'),
    Input('shift-key', 'n_clicks'),
    State('shift-state', 'data')
)
def update_keyboard(n_clicks, shift_state):
    shift_state = not shift_state
    return create_keyboard(shift=shift_state)


@app.callback(
    Output('shift-state', 'data'),
    Input('shift-key', 'n_clicks'),
    State('shift-state', 'data')
)
def update_shift_state(n_clicks, shift_state):
    return not shift_state


@app.callback(
    Output('modal', 'is_open'),
    Output('show-survey', 'data'),
    Output('error-message', 'children'),
    Output('satisfaction', 'value'),
    Output('comments', 'value'),
    Input('interval-component', 'n_intervals'),
    Input('submit-survey', 'n_clicks'),
    Input({'type': 'key', 'index': ALL}, 'n_clicks'),
    State('satisfaction', 'value'),
    State('comments', 'value'),
    State('show-survey', 'data'),
    State('modal', 'is_open'),
)
def update_modal_and_comments(n_intervals, n_clicks_submit, n_clicks_keys, satisfaction, comments, show_survey,
                              is_open):
    if comments is None:
        comments = ''

    triggered = ctx.triggered_id

    if triggered and isinstance(triggered, dict) and triggered['type'] == 'key':
        key = triggered['index']
        if key == 'Backspace':
            comments = comments[:-1]
        elif key != 'Shift':
            comments += key
        return is_open, show_survey, '', satisfaction, comments

    if triggered == 'interval-component':
        return True, False, '', None, ''  # Show survey, reset flag and form fields, clear error message

    if triggered == 'submit-survey':
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
def update_dashboard_content(n_clicks, satisfaction, comments):
    return html.Div([
        html.H3('Welcome to the Dashboard', style={'fontSize': '32px'}),
        html.Hr(),
        # Here you can add the initial dashboard content
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
