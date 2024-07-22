import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import os

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the CSV file path
csv_file_path = 'survey_results.csv'

# Check if the CSV file exists, and if not, create it with the correct headers
if not os.path.isfile(csv_file_path):
    df = pd.DataFrame(columns=['Timestamp', 'Satisfaction', 'Comments'])
    df.to_csv(csv_file_path, index=False)

# Layout of the app
app.layout = html.Div([
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0),  # 10 minutes interval
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
                    dcc.Textarea(id='comments', style={'width': '100%', 'height': '150px'}),
                    html.Div(id='error-message', style={'color': 'red', 'marginTop': '10px'})
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
    ]),
    dcc.Input(id='hidden-keyboard-trigger', style={'display': 'none'})
])

@app.callback(
    Output('modal', 'is_open'),
    Output('show-survey', 'data'),
    Output('error-message', 'children'),
    Output('satisfaction', 'value'),
    Output('comments', 'value'),
    Output('hidden-keyboard-trigger', 'value'),
    Input('interval-component', 'n_intervals'),
    Input('submit-survey', 'n_clicks'),
    Input('comments', 'n_clicks'),
    State('satisfaction', 'value'),
    State('comments', 'value'),
    State('show-survey', 'data'),
    State('modal', 'is_open'),
)
def toggle_modal(n_intervals, n_clicks, comments_n_clicks, satisfaction, comments, show_survey, is_open):
    trigger = ctx.triggered_id
    
    if trigger == 'interval-component':
        return True, False, '', None, '', ''  # Show survey, reset flag and form fields, clear error message, clear hidden input

    if trigger == 'submit-survey':
        if satisfaction:
            # Save the survey results to the CSV file
            new_data = pd.DataFrame({
                'Timestamp': [pd.Timestamp.now()],
                'Satisfaction': [satisfaction],
                'Comments': [comments]
            })
            new_data.to_csv(csv_file_path, mode='a', header=False, index=False)
            return False, True, '', None, '', ''  # Close survey, set flag, clear error message and form fields, clear hidden input
        else:
            return True, False, 'Please answer all required questions.', satisfaction, comments, ''  # Show error message, clear hidden input

    if trigger == 'comments':
        os.system('wvkbd-mobintl')
        return is_open, show_survey, '', satisfaction, comments, 'triggered'  # Set hidden input value to trigger keyboard

    return is_open, show_survey, '', satisfaction, comments, ''  # Clear hidden input

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
        ])
    else:
        return html.Div([
            html.H3('Welcome to the Dashboard'),
            html.Hr(),
            # Here you can add the initial dashboard content
        ])

if __name__ == '__main__':
    app.run_server(debug=True)
