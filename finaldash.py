import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import pandas as pd
import plotly.graph_objs as go
import datetime
from dash import callback_context

# Paths to the SQLite databases
db_path = '/home/mainhubs/pm25_data.db'  # Replace with the correct path to your database
DATABASE_PATH = 'fan_state.db'

# Initialize the Dash app
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True,
                prevent_initial_callbacks=True)

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('relay_status.db')
cursor = conn.cursor()

# Define a script with multiple CREATE TABLE statements
create_tables_script = """
CREATE TABLE IF NOT EXISTS Outdoor (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER
);

CREATE TABLE IF NOT EXISTS Indoor (
    id INTEGER PRIMARY KEY,
    description TEXT,
    price REAL
);

CREATE TABLE IF NOT EXISTS UserControl (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (product_id) REFERENCES table2 (id)
);

CREATE TABLE IF NOT EXISTS FanControl (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (product_id) REFERENCES table2 (id)
);

CREATE TABLE IF NOT EXISTS Baseline (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (product_id) REFERENCES table2 (id)
);
"""
# Execute the script
cursor.executescript(create_tables_script)
conn.commit()
conn.close()

# Layout for the main dashboard with gauges
def dashboard_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("CURRENT CONDITIONS", className="text-center text-dark mb-4"), width=12)
        ]),
        dbc.Row([
            dbc.Col(html.Div([
                html.H3("Inside", className="text-center text-warning mb-3"),
                dcc.Graph(id="indoor-gauge"),
                html.Div(id="indoor-value", className="display-4 text-center text-dark mt-2")
            ]), width=6, className="border-right"),
            dbc.Col(html.Div([
                html.H3("Outside", className="text-center text-info mb-3"),
                dcc.Graph(id="outdoor-gauge"),
                html.Div(id="outdoor-value", className="display-4 text-center text-dark mt-2")
            ]), width=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(html.H3("Filter State", className="text-center text-success")),
            dbc.Col(html.Div(id="filter-state", className="display-4 text-center text-dark mt-2")),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Link("Go to Filtration Control", href='/control', className="btn btn-primary mt-4"), width=12)
        ]),
        dcc.Interval(id='interval-component', interval=10 * 1000, n_intervals=0)
    ], fluid=True, className="p-4")

# Callback for updating the dashboard with gauge and PM2.5 values
@app.callback(
    [
        Output('outdoor-value', 'children'),
        Output('indoor-value', 'children'),
        Output('filter-state', 'children'),
        Output('outdoor-gauge', 'figure'),
        Output('indoor-gauge', 'figure')
    ],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    # Connect to the database
    conn = sqlite3.connect(db_path)

    # SQL queries
    outdoor_pm25_query = "SELECT timestamp, pm25_value FROM pm25_data ORDER BY timestamp DESC LIMIT 1;"
    indoor_pm25_query = "SELECT timestamp, pm25 FROM Indoor ORDER BY timestamp DESC LIMIT 1;"
    filter_state_query = "SELECT filter_state FROM filter_state ORDER BY timestamp DESC LIMIT 1;"

    try:
        outdoor_pm25_data = pd.read_sql(outdoor_pm25_query, conn)
        indoor_pm25_data = pd.read_sql(indoor_pm25_query, conn)
        filter_state = conn.execute(filter_state_query).fetchone()[0] if conn.execute(filter_state_query).fetchone() else "Unknown"
    except Exception:
        outdoor_pm25_data = pd.DataFrame(columns=['timestamp', 'pm25_value'])
        indoor_pm25_data = pd.DataFrame(columns=['timestamp', 'pm25'])
        filter_state = "Unknown"
    finally:
        conn.close()

    outdoor_value = int(round(outdoor_pm25_data['pm25_value'].iloc[0])) if not outdoor_pm25_data.empty else "No Data"
    indoor_value = int(round(indoor_pm25_data['pm25'].iloc[0])) if not indoor_pm25_data.empty else "No Data"

    # Create gauge figures for outdoor and indoor PM2.5 levels
    outdoor_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=outdoor_value if outdoor_value != "No Data" else 0,
        title={'text': "Outdoor PM2.5"},
        gauge={'axis': {'range': [0, 500]}, 'bar': {'color': "blue"}}
    ))
    indoor_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=indoor_value if indoor_value != "No Data" else 0,
        title={'text': "Indoor PM2.5"},
        gauge={'axis': {'range': [0, 500]}, 'bar': {'color': "orange"}}
    ))

    return str(outdoor_value), str(indoor_value), filter_state, outdoor_gauge, indoor_gauge


# Layout for the fan control page with modals
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

        dbc.Modal([dbc.ModalHeader("Confirm Your Action"),
                   dbc.ModalBody("Did you intend to press the 'Disable Fan' button?"),
                   dbc.ModalFooter([
                       dbc.Button("Yes (Continue to Disable)", id="confirm-yes", className="btn btn-primary", n_clicks=0),
                       dbc.Button("No (Cancel Disable)", id="confirm-no", className="btn btn-secondary", n_clicks=0)])],
                  id="modal-confirm", is_open=False, backdrop="static", size="lg", centered=True),

        dbc.Modal([dbc.ModalHeader("Action Canceled"),
                   dbc.ModalBody("The 'Disable Fan' command was canceled."),
                   dbc.ModalFooter(dbc.Button("Close", id="close-cancel", className="btn btn-secondary", n_clicks=0))],
                  id="modal-cancel", is_open=False, backdrop="static", size="lg", centered=True),

        dbc.Modal([dbc.ModalHeader("Warning", style={'backgroundColor': '#f0f0f0', 'color': 'red'}),
                   dbc.ModalBody("Disabling the fan may affect air quality. Do you want to continue?"),
                   dbc.ModalFooter([
                       dbc.Button("Yes (Continue to Disable)", id="warning-yes", className="btn btn-primary", n_clicks=0),
                       dbc.Button("No (Cancel)", id="warning-no", className="btn btn-secondary", n_clicks=0)])],
                  id="modal-warning", is_open=False, backdrop="static", size="lg", centered=True),

        dbc.Modal([dbc.ModalHeader("Notification"),
                   dbc.ModalBody("The fan is now enabled and will filter the air."),
                   dbc.ModalFooter(dbc.Button("Close", id="close-notification-on", className="btn btn-secondary", n_clicks=0))],
                  id="modal-notification-on", is_open=False, backdrop="static", size="lg", centered=True),

        dcc.Interval(id='interval-timer', interval=10 * 1000, n_intervals=0, disabled=True),
        dcc.Store(id='workflow-state', data={'stage': 'initial'}),
        dcc.Link("Back to Dashboard", href='/', className="btn btn-secondary mt-4")
    ])

# Helper function for last fan state
def get_last_state_from_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT state FROM fan_state ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "OFF"
    except sqlite3.Error:
        return "OFF"

# Update fan state in database
def update_fan_state(state):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO fan_state (state, timestamp) VALUES (?, ?)', (state, timestamp))
    conn.commit()
    conn.close()

# Modal handling callback
@app.callback(
    [Output('modal-confirm', 'is_open'),
     Output('modal-cancel', 'is_open'),
     Output('modal-warning', 'is_open'),
     Output('modal-notification-on', 'is_open'),
     Output('interval-timer', 'disabled'),
     Output('disable-fan', 'children'),
     Output('disable-fan', 'className'),
     Output('workflow-state', 'data')],
    [Input('disable-fan', 'n_clicks'),
     Input('confirm-yes', 'n_clicks'),
     Input('confirm-no', 'n_clicks'),
     Input('warning-yes', 'n_clicks'),
     Input('warning-no', 'n_clicks'),
     Input('close-cancel', 'n_clicks'),
     Input('close-notification-on', 'n_clicks')],
    [State('workflow-state', 'data')]
)
def handle_modals(disable_fan_clicks, confirm_yes_clicks, confirm_no_clicks, warning_yes_clicks, warning_no_clicks,
                  close_cancel_clicks, close_notification_on_clicks, workflow_state):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0] if callback_context.triggered else None

    # Modal and button state initialization
    confirm_modal_open = False
    cancel_modal_open = False
    warning_modal_open = False
    notification_on_modal_open = False
    interval_disabled = True

    # Workflow logic
    stage = workflow_state.get('stage', 'initial')
    button_text = "Turn Fan On" if stage == 'fan_off' else "Disable Fan"
    button_class = "btn btn-success btn-lg" if stage == 'fan_off' else "btn btn-danger btn-lg"

    # Trigger actions based on button clicks
    if triggered_id == 'disable-fan':
        if stage == 'fan_off':
            update_fan_state('ON')
            notification_on_modal_open = True
            stage = 'initial'
        else:
            confirm_modal_open = True
            stage = 'confirm'
    elif triggered_id == 'confirm-yes':
        confirm_modal_open = False
        warning_modal_open = True
        stage = 'warning'
    elif triggered_id == 'warning-yes':
        update_fan_state('OFF')
        stage = 'fan_off'
        interval_disabled = False
        button_text = "Turn Fan On"
        button_class = "btn btn-success btn-lg"
    elif triggered_id in ['warning-no', 'confirm-no', 'close-cancel']:
        stage = 'initial'

    return (confirm_modal_open, cancel_modal_open, warning_modal_open, notification_on_modal_open,
            interval_disabled, button_text, button_class, {'stage': stage})


# Layout setup with page navigation
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/control':
        return control_workflow_layout()
    else:
        return dashboard_layout()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
