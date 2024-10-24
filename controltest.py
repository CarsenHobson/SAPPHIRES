import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import datetime
from dash import callback_context

# Initialize the Dash app with the SLATE theme and allow for callback exceptions
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Database setup
DATABASE_PATH = 'fan_state.db'

def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fan_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT NOT NULL CHECK (state IN ('ON', 'OFF')),
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def update_fan_state(state):
    """Update the fan state in the database with the current timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO fan_state (state, timestamp)
        VALUES (?, ?)
    ''', (state, timestamp))
    conn.commit()
    conn.close()

def get_last_state_from_db():
    """Retrieve the last state from the SQLite database."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT state FROM fan_state ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    return "OFF"  # Default state if no log exists, meaning the fan starts as off.

def log_action(action):
    """Log an action with a timestamp to the fan decision log."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("fan_decision_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} - {action}\n")

# Initialize the database
init_db()

# Define the dashboard layout
def dashboard_layout():
    return dbc.Container([
        html.H1("Dashboard Page", className="text-center"),
        html.P("This is the main dashboard with overview statistics.", className="text-center"),
        dcc.Link("Go to Filtration Control", href='/control', className="btn btn-primary mt-4")
    ], fluid=True, className="p-4")

# Define the control workflow layout for managing the fan state
def control_workflow_layout():
    last_state = get_last_state_from_db()
    button_text = "Disable Fan" if last_state == "ON" else "Turn Fan On"
    button_color = "danger" if last_state == "ON" else "success"

    return html.Div([
        html.Div(id='disable-fan-div', children=[
            html.Button(button_text, id='disable-fan', className=f"btn btn-{button_color} btn-lg",
                        style={'width': '200px', 'height': '200px', 'border-radius': '50%', 'font-size': '20px',
                               'text-align': 'center', 'line-height': '160px'})
        ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'min-height': '100vh'}),

        # Step 1 Modal for confirmation of disabling fan
        dbc.Modal(
            [
                dbc.ModalHeader("Confirm Your Action", style={'backgroundColor': '#f0f0f0', 'color': 'black'}),
                dbc.ModalBody("Did you intend to press the 'Disable Fan' button?",
                              style={'backgroundColor': '#f0f0f0', 'color': 'black'}),
                dbc.ModalFooter([
                    dbc.Button("Yes (Continue to Disable)", id="confirm-yes", className="btn btn-primary", n_clicks=0),
                    dbc.Button("No (Cancel Disable)", id="confirm-no", className="btn btn-secondary", n_clicks=0)
                ], style={'backgroundColor': '#f0f0f0'})
            ],
            id="modal-confirm",
            is_open=False,
        ),

        # Message Modal for canceling the action
        dbc.Modal(
            [
                dbc.ModalHeader("Action Canceled", style={'backgroundColor': '#f0f0f0', 'color': 'black'}),
                dbc.ModalBody(
                    "The 'Disable Fan' command was canceled. The fan is currently filtering the air and improving the air quality in your residence. You may now close this window.",
                    style={'backgroundColor': '#f0f0f0', 'color': 'black'}
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-cancel", className="btn btn-secondary", n_clicks=0),
                    style={'backgroundColor': '#f0f0f0'}
                )
            ],
            id="modal-cancel",
            is_open=False,
        ),

        # Step 2 Modal for warning step
        dbc.Modal(
            [
                dbc.ModalHeader("Disclaimer", style={'backgroundColor': '#f0f0f0', 'color': 'red'}),
                dbc.ModalBody(
                    "Proceeding further will disable the fan, which will filter and improve air quality in your residence. Doing so may result in harmful or hazardous conditions. Do you want to proceed?",
                ),
                dbc.ModalFooter([
                    dbc.Button("Yes (Continue to Disable)", id="warning-yes", className="btn btn-primary", n_clicks=0),
                    dbc.Button("No (Cancel Disable)", id="warning-no", className="btn btn-secondary", n_clicks=0)
                ], style={'backgroundColor': '#f0f0f0'})
            ],
            id="modal-warning",
            is_open=False,
        ),

        # Modal for confirming turning the fan on
        dbc.Modal(
            [
                dbc.ModalHeader("Confirm Your Action", style={'backgroundColor': '#f0f0f0', 'color': 'black'}),
                dbc.ModalBody("Did you intend to turn the fan on?",
                              style={'backgroundColor': '#f0f0f0', 'color': 'black'}),
                dbc.ModalFooter([
                    dbc.Button("Yes (Turn Fan On)", id="confirm-on-yes", className="btn btn-primary", n_clicks=0),
                    dbc.Button("No (Cancel)", id="confirm-on-no", className="btn btn-secondary", n_clicks=0)
                ], style={'backgroundColor': '#f0f0f0'})
            ],
            id="modal-confirm-on",
            is_open=False,
        ),

        # Notification modal after turning the fan on
        dbc.Modal(
            [
                dbc.ModalHeader("Notification", style={'backgroundColor': '#f0f0f0', 'color': 'black'}),
                dbc.ModalBody(
                    "You have selected the 'Enable Fan' button. The fan will turn on momentarily and will proceed filtering the air and improving the air quality in your residence. You may now close this window.",
                    style={'backgroundColor': '#f0f0f0', 'color': 'black'}
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-notification-on", className="btn btn-secondary", n_clicks=0),
                    style={'backgroundColor': '#f0f0f0'}
                )
            ],
            id="modal-notification-on",
            is_open=False,
        ),

        # Step 3 Modal for countdown before disabling the fan
        dbc.Modal(
            [
                dbc.ModalHeader("Fan Disabling Process", style={'backgroundColor': '#f0f0f0', 'color': 'black'}),
                dbc.ModalBody(
                    "The disabling process is underway. If you choose to cancel, please do so by clicking the button below before the timer runs out.",
                    style={'backgroundColor': '#f0f0f0', 'color': 'black'}
                ),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-timer", className="btn btn-danger", n_clicks=0),
                ], style={'backgroundColor': '#f0f0f0'})
            ],
            id="modal-countdown",
            is_open=False,
        ),

        # CAUTION modal after fan is disabled
        dbc.Modal(
            [
                dbc.ModalHeader("CAUTION", style={'backgroundColor': '#f0f0f0', 'color': 'red'}),
                dbc.ModalBody(
                    "The fan has now been turned off. Please note that you may be exposed to harmful or hazardous conditions due to the decrease in air quality. Please refer to the Information Tab for more information and recommended actions. To turn on the fan again, please close the window and press the button again to initiate filtering air.",
                    style={'backgroundColor': '#f0f0f0', 'color': 'black'}
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-caution", className="btn btn-secondary", n_clicks=0),
                    style={'backgroundColor': '#f0f0f0'}
                )
            ],
            id="modal-caution",
            is_open=False,
        ),

        # Interval component for 10-second countdown
        dcc.Interval(id='interval-timer', interval=10*1000, n_intervals=0, disabled=True),

        # Store components to manage state and modals
        dcc.Store(id='workflow-state', data={'stage': 'initial'}),

        # Link to navigate back to the dashboard
        dcc.Link("Back to Dashboard", href='/', className="btn btn-secondary mt-4")
    ])

# Define the main app layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')  # Placeholder for content that changes with the URL
])

# Callback to update the content based on the URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/control':
        return control_workflow_layout()
    else:
        return dashboard_layout()

# Callback to manage modal flow and stage transitions
@app.callback(
    [Output('modal-confirm', 'is_open'),
     Output('modal-cancel', 'is_open'),
     Output('modal-warning', 'is_open'),
     Output('modal-confirm-on', 'is_open'),
     Output('modal-notification-on', 'is_open'),
     Output('modal-countdown', 'is_open'),
     Output('modal-caution', 'is_open'),
     Output('interval-timer', 'disabled'),
     Output('disable-fan', 'children'),
     Output('disable-fan', 'className'),
     Output('workflow-state', 'data')],
    [Input('disable-fan', 'n_clicks'),
     Input('confirm-yes', 'n_clicks'),
     Input('confirm-no', 'n_clicks'),
     Input('close-cancel', 'n_clicks'),
     Input('warning-yes', 'n_clicks'),
     Input('warning-no', 'n_clicks'),
     Input('confirm-on-yes', 'n_clicks'),
     Input('confirm-on-no', 'n_clicks'),
     Input('close-notification-on', 'n_clicks'),
     Input('close-caution', 'n_clicks'),
     Input('cancel-timer', 'n_clicks'),
     Input('interval-timer', 'n_intervals')],
    [State('disable-fan', 'children'),
     State('workflow-state', 'data')]
)
def handle_modals(disable_fan_clicks, confirm_yes_clicks, confirm_no_clicks, close_cancel_clicks, warning_yes_clicks,
                  warning_no_clicks, confirm_on_yes_clicks, confirm_on_no_clicks, close_notification_on_clicks,
                  close_caution_clicks, cancel_timer_clicks, n_intervals, button_text, workflow_state):
    # Determine which input triggered the callback
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0] if callback_context.triggered else None

    # Initialize modal states
    confirm_modal_open = False
    cancel_modal_open = False
    warning_modal_open = False
    confirm_on_modal_open = False
    notification_on_modal_open = False
    countdown_modal_open = False
    caution_modal_open = False
    interval_disabled = True
    stage = workflow_state.get('stage', 'initial')
    button_class = "btn btn-danger btn-lg" if button_text == "Disable Fan" else "btn btn-success btn-lg"

    # Handle the "Disable Fan" button click
    if triggered_id == 'disable-fan' and stage == 'initial':
        if button_text == "Disable Fan":
            confirm_modal_open = True
            stage = 'confirm'
            log_action("Clicked 'Disable Fan'")
        elif button_text == "Turn Fan On":
            confirm_on_modal_open = True
            stage = 'confirm_on'
            log_action("Clicked 'Turn Fan On'")

    # Handle confirmation modal "Yes" for turning the fan on
    elif triggered_id == 'confirm-on-yes' and stage == 'confirm_on':
        update_fan_state("ON")
        button_text = "Disable Fan"
        button_class = "btn btn-danger btn-lg"
        notification_on_modal_open = True  # Show the notification modal
        stage = 'initial'
        log_action("Fan enabled")

    # Close the notification modal when the user clicks close
    elif triggered_id == 'close-notification-on':
        notification_on_modal_open = False
        stage = 'initial'

    # Handle any cancellations (e.g., "No" in any confirmation modal)
    elif triggered_id in ['confirm-no', 'confirm-on-no', 'warning-no', 'cancel-timer']:
        cancel_modal_open = True
        stage = 'initial'
        log_action("Action canceled")
        last_state = get_last_state_from_db()
        button_text = "Disable Fan" if last_state == "ON" else "Turn Fan On"
        button_class = "btn btn-danger btn-lg" if last_state == "ON" else "btn btn-success btn-lg"

    # Close the "Action Canceled" modal when the user clicks the close button
    elif triggered_id == 'close-cancel':
        cancel_modal_open = False
        stage = 'initial'
        log_action("Closed Action Canceled modal")

    # Handle confirmation modal "Yes" for disabling the fan
    elif triggered_id == 'confirm-yes' and stage == 'confirm':
        confirm_modal_open = False
        warning_modal_open = True
        stage = 'warning'
        log_action("Confirmed 'Yes' on Disable")

    # Handle warning modal "Yes"
    elif triggered_id == 'warning-yes' and stage == 'warning':
        warning_modal_open = False
        countdown_modal_open = True
        interval_disabled = False  # Start the interval to begin countdown
        stage = 'countdown'
        log_action("Confirmed 'Yes' on Warning")

    # Handle the end of the countdown (turn fan off)
    elif triggered_id == 'interval-timer' and stage == 'countdown' and n_intervals > 0:
        countdown_modal_open = False
        caution_modal_open = True  # Show the CAUTION modal after countdown ends
        interval_disabled = True  # Stop the interval after it has triggered
        button_text = "Turn Fan On"
        button_class = "btn btn-success btn-lg"
        stage = 'initial'
        log_action("Fan disabled after countdown")
        update_fan_state("OFF")

    # Close the caution modal when the user clicks close
    elif triggered_id == 'close-caution':
        caution_modal_open = False
        stage = 'initial'

    return (confirm_modal_open, cancel_modal_open, warning_modal_open, confirm_on_modal_open,
            notification_on_modal_open, countdown_modal_open, caution_modal_open, interval_disabled,
            button_text, button_class, {'stage': stage})

# Run the app
if __name__ == '__main__':
