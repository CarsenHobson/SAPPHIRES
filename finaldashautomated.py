import dash
from dash import dcc, html, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import pandas as pd
import plotly.graph_objs as go
import datetime
import base64

# Paths to the SQLite databases
db_path = '/home/mainhubs/SAPPHIRES.db'  # Replace with the correct path to your database


app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP, "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap"],
                suppress_callback_exceptions=True)

# Improved color scheme
BACKGROUND_COLOR = "#f0f2f5"
PRIMARY_COLOR = "#FFFFCB"
SUCCESS_COLOR = "#28a745"
WARNING_COLOR = "#ffc107"
DANGER_COLOR = "#dc3545"


# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Define a script with multiple CREATE TABLE statements
create_tables_script = """
CREATE TABLE IF NOT EXISTS Indoor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    pm25 REAL,
    temperature REAL,
    humidity REAL
);

CREATE TABLE IF NOT EXISTS baseline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    baseline_value REAL
);

CREATE TABLE IF NOT EXISTS user_control (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    user_input TEXT
);

CREATE TABLE IF NOT EXISTS filter_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    filter_state TEXT
);

CREATE TABLE IF NOT EXISTS Outdoor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    pm25_value REAL,
    temperature REAL,
    humidity REAL,
    wifi_strength REAL
);
"""
# Execute the script
cursor.executescript(create_tables_script)
conn.commit()
conn.close()

def encode_image(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{encoded}"

# Paths to the images you uploaded
emoji_paths = {
    "good": "/home/mainhubs/good.png",
    "moderate": "/home/mainhubs/moderate.png",
    "unhealthy_sensitive": "/home/mainhubs/unhealthy_sensitive.png",
    "unhealthy": "/home/mainhubs/unhealthy.png",
    "very_unhealthy": "/home/mainhubs/very_unhealthy.png",
    "hazardous": "/home/mainhubs/hazardous.png"
}

# Helper function to select image based on AQI
def get_aqi_emoji(aqi):
    if aqi <= 25:
        return encode_image(emoji_paths["good"])
    elif 26 <= aqi <= 50:
        return encode_image(emoji_paths["moderate"])
    elif 51 <= aqi <= 75:
        return encode_image(emoji_paths["unhealthy_sensitive"])
    elif 76 <= aqi <= 100:
        return encode_image(emoji_paths["unhealthy"])
    elif 101 <= aqi <= 125:
        return encode_image(emoji_paths["very_unhealthy"])
    else:
        return encode_image(emoji_paths["hazardous"])

# Function to determine gauge color based on AQI level
def get_gauge_color(aqi):
    if aqi <= 25:
        return "green"
    elif 26 <= aqi <= 50:
        return "yellow"
    elif 51 <= aqi <= 75:
        return "orange"
    elif 76 <= aqi <= 100:
        return "#ff6600"  # Dark orange
    elif 101 <= aqi <= 125:
        return "red"
    else:
        return "#8b0000"  # Dark red for hazardous levels

def dashboard_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                html.H1(
                    "CURRENT CONDITIONS", 
                    className="text-center mb-0",  
                    style={
                        "font-family": "Roboto, sans-serif", 
                        "font-weight": "700", 
                        "color": "black", 
                        "font-size": "2.5rem", 
                        "background-color": PRIMARY_COLOR, 
                        "padding": "20px",
                        "border": "2px solid black",
                        "border-radius": "10px 10px 0 0"
                    }
                ), 
                width=12
            )
        ], className="g-0"),  

            # Main content row with cards
        dbc.Row([
            # Inside AQI card with Temperature box
            dbc.Col(dbc.Card([
                dbc.CardHeader("INSIDE", className="text-center mb-0",
                               style={
                                   "font-size": "1.5rem",
                                   "font-weight": "700",
                                   "color": "black",
                                   "background": "white",
                                   "border-bottom": "2px solid black",
                                   "border-right": "2px solid black",
                                   "border-left": "2px solid black"
                               }),
                html.Div([
                    # Top two-thirds with black border
                    html.Div([
                        dcc.Graph(id="indoor-gauge", config={"displayModeBar": False})
                    ], style={
                        "padding": "30px",
                        "border": "2px solid black",
                        "border-top": "none",
                        "border-bottom": "none",
                        "height": "455px"  # Adjust height for top two-thirds
                    }),
                   
                # Bottom third with temperature box
                # Bottom third with temperature box
                html.Div([
                    # Temperature box wrapper
                    html.Div([
                        # Header for Temperature box
                        html.Div("Temperature", className="text-center",
                                 style={
                                     "font-size": "1.5rem",
                                     "font-weight": "bold",
                                     "padding-top": "10px",
                                     "color": "black"
                                 }),
                        # Temperature display for indoor temperature
                        html.Div(id="indoor-temp-display",  # Indoor temperature display ID
                                 className="d-flex justify-content-center align-items-center",
                                 style={
                                     "font-size": "2rem",
                                     "color": "black",
                                     "text-align": "center",
                                     "margin-top": "10px"  # Adds spacing between header and value
                                 })
                    ], style={
                        "width": "400px",
                        "height": "150px",
                        "border": "2px solid black",
                        "position": "absolute",
                        "bottom": "0",
                        "left": "0",
                        "background-color": "#D2B48C",
                        "border-radius": "5px 7px 5px 0",
                        "display": "flex",
                        "flex-direction": "column",
                        "justify-content": "center",
                        "align-items": "center"
                    })
                ], style={
                    "padding": "30px",
                    "border-left": "2px solid black",
                    "border-right": "2px solid black",
                    "border-bottom": "2px solid black",
                    "height": "227px",
                    "background-color": "transparent"
                })



                ])
            ]), width=6, className="p-0"),

            # Outside AQI card with Temperature box
            dbc.Col(dbc.Card([
                dbc.CardHeader("OUTSIDE", className="text-center mb-0",
                               style={
                                   "font-size": "1.5rem",
                                   "font-weight": "700",
                                   "color": "black",
                                   "background": "white",
                                   "border-bottom": "2px solid black",
                                   "border-right": "2px solid black",
                                   "border-left": "2px solid black",
                               }),
                html.Div([
                    # Top two-thirds with black border
                    html.Div([
                        dcc.Graph(id="outdoor-gauge", config={"displayModeBar": False})
                    ], style={
                        "padding": "30px",
                        "border": "2px solid black",
                        "border-top": "none",
                        "border-bottom": "none",
                        "height": "455px"  # Adjust height for top two-thirds
                    }),
                   
                # Bottom third with temperature box
                html.Div([
                    # Temperature box wrapper
                    html.Div([
                        # Header for Temperature box
                        html.Div("Temperature", className="text-center",
                                 style={
                                     "font-size": "1.5rem",
                                     "font-weight": "bold",
                                     "padding-top": "10px",
                                     "color": "black"
                                 }),
                        # Temperature display for outdoor temperature
                        html.Div(id="outdoor-temp-display",  # Outdoor temperature display ID
                                 className="d-flex justify-content-center align-items-center",
                                 style={
                                     "font-size": "2rem",
                                     "color": "black",
                                     "text-align": "center",
                                     "margin-top": "10px"  # Adds spacing between header and value
                                 })
                    ], style={
                        "width": "400px",
                        "height": "150px",
                        "border": "2px solid black",
                        "position": "absolute",
                        "bottom": "0",
                        "right": "0",
                        "background-color": "#7BC8F6",
                        "border-radius": "7px 5px 5px 0",
                        "display": "flex",
                        "flex-direction": "column",
                        "justify-content": "center",
                        "align-items": "center"
                    })
                ], style={
                    "padding": "30px",
                    "border-left": "2px solid black",
                    "border-right": "2px solid black",
                    "border-bottom": "2px solid black",
                    "height": "227px",
                    "background-color": "transparent"
                })



                ])
            ]), width=6, className="p-0")]),


        # Centered Fan Control Button with border aligned to bottom of cards
        dbc.Row([
            html.Div(
                html.Button("Override Fan", id="disable-fan", 
                            className="btn btn-danger btn-lg", 
                            style={
                                "width": "200px",
                                "height": "100px",
                                "border-radius": "200px", 
                                "font-size": "1.8rem",
                                "text-color": "yellow"
                            }),
                style={
                    "border": "2px solid black",  # Add border around the button container
                    "padding": "10px", 
                    "width": "300px", 
                    "height": "200px",
                    "position": "absolute",  # Absolute positioning
                    "left": "50%",  # Center horizontally
                    "transform": "translateX(-50%)",  # Adjust for true centering
                    "bottom": "683px",  # Align to the bottom of the parent container
                    "display": "flex",  # Use flexbox to center content
                    "align-items": "center",  # Center vertically
                    "justify-content": "center",  # Center horizontally
                    "text-align": "center",
                    "box-sizing": "border-box",  # Ensure padding does not affect width
                    "background-color": "black",
                    "border-radius": "7px" # Background to make the button stand out
                }
            )
        ], style={"position": "relative", "height": "682px"}, className="g-0"),


        # Modal for confirmation and notification
        dbc.Modal([
            dbc.ModalHeader("Confirm Action"),
            dbc.ModalBody("Are you sure you want to disable the fan?"),
            dbc.ModalFooter([
                dbc.Button("Yes", id="confirm-yes", className="btn btn-primary"),
                dbc.Button("No", id="confirm-no", className="btn btn-secondary")
            ])
        ], id="modal-confirm", is_open=False, backdrop="static", centered=True),
        
        dbc.Modal([
            dbc.ModalHeader("Warning", style={'color': 'red'}),
            dbc.ModalBody("Disabling the fan may affect air quality. Do you want to proceed?"),
            dbc.ModalFooter([
                dbc.Button("Proceed", id="warning-yes", className="btn btn-danger"),
                dbc.Button("Cancel", id="warning-no", className="btn btn-secondary")
            ])
        ], id="modal-warning", is_open=False, backdrop="static", centered=True),

        dbc.Modal([
            dbc.ModalHeader("Fan Enabled"),
            dbc.ModalBody("You have selected the 'Enable Fan' button. The fan will turn on momentarily and will proceed filtering the air and improving the air quality in your residence. You may now close this window."),
            dbc.ModalFooter(dbc.Button("Close", id="close-notification", className="btn btn-secondary"))
        ], id="modal-notification", is_open=False, backdrop="static", centered=True),

        dcc.Interval(id='interval-component', interval=10 * 1000, n_intervals=0),
        dcc.Store(id='workflow-state', data={'stage': 'initial'})
    ], fluid=True, className="p-4")


@app.callback(
    [Output('indoor-gauge', 'figure'),
     Output('outdoor-gauge', 'figure'),
     Output('indoor-temp-display', 'children'),
     Output('outdoor-temp-display', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    conn = sqlite3.connect(db_path)
    
    try:
        # Fetch the latest and past 3 indoor and outdoor AQI readings
        indoor_pm = pd.read_sql("SELECT pm25 FROM Indoor ORDER BY timestamp DESC LIMIT 60;", conn)
        outdoor_pm = pd.read_sql("SELECT pm25_value FROM Outdoor ORDER BY timestamp DESC LIMIT 60;", conn)
        
        # Fetch the latest temperature readings
        indoor_temp = pd.read_sql("SELECT temperature FROM Indoor ORDER BY timestamp DESC LIMIT 1;", conn)
        outdoor_temp = pd.read_sql("SELECT temperature FROM Outdoor ORDER BY timestamp DESC LIMIT 1;", conn)
        
        # Determine AQI values and calculate delta
        indoor_aqi = round(int(indoor_pm['pm25'].iloc[0]))
        outdoor_aqi = round(int(outdoor_pm['pm25_value'].iloc[0]))
        indoor_aqi_avg = indoor_pm['pm25'].iloc[30:].mean()
        outdoor_aqi_avg = outdoor_pm['pm25_value'].iloc[30:].mean()
        indoor_delta = indoor_aqi - round(indoor_aqi_avg)
        outdoor_delta = outdoor_aqi - round(outdoor_aqi_avg)
        
        # Fetch and format temperature values
        indoor_temp_value = round(indoor_temp['temperature'].iloc[0], 1)
        outdoor_temp_value = round(outdoor_temp['temperature'].iloc[0], 1)
        indoor_temp_text = f"{indoor_temp_value} °F"
        outdoor_temp_text = f"{outdoor_temp_value} °F"
    except Exception as e:
        print(f"Error retrieving data: {e}")
        indoor_aqi, outdoor_aqi, indoor_delta, outdoor_delta = 0, 0, 0, 0
        indoor_temp_text, outdoor_temp_text = "N/A", "N/A"
    finally:
        conn.close()

    # Determine arrow direction and color
    indoor_arrow = "⬆️" if indoor_delta > 0 else "⬇️"
    indoor_arrow_color = "green" if indoor_delta < 0 else "red"
    outdoor_arrow = "⬆️" if outdoor_delta > 0 else "⬇️"
    outdoor_arrow_color = "green" if outdoor_delta < 0 else "red"
    
    # Format delta text with "+" or "-" sign
    indoor_delta_text = f"+{indoor_delta}" if indoor_delta > 0 else str(indoor_delta)
    outdoor_delta_text = f"+{outdoor_delta}" if outdoor_delta > 0 else str(outdoor_delta)

    # Get emojis
    indoor_emoji = get_aqi_emoji(indoor_aqi)
    outdoor_emoji = get_aqi_emoji(outdoor_aqi)

    # Position offset functions for dynamic placements
    def get_position_offset(value):
        length = len(str(value))
        return 0.48 if length == 1 else 0.47 if length == 2 else 0.46

    def arrow_position_offset(value):
        length = len(str(value))
        return 0.55 if length == 1 else 0.58 if length == 2 else 0.59

    # Indoor gauge with dynamic number placement
    indoor_gauge = go.Figure(go.Indicator(
        mode="gauge",
        value=indoor_aqi,
        gauge={
            'axis': {'range': [0, 150]},
            'bar': {'color': get_gauge_color(indoor_aqi)},
            'bgcolor': "lightgray",
            'bordercolor': "black",
        }
    ))

    indoor_gauge.add_annotation(
        x=get_position_offset(indoor_aqi),
        y=0,
        text=f"<b>{indoor_aqi}</b>",
        showarrow=False,
        font=dict(size=70, color="black"),
        xanchor="center",
        yanchor="bottom"
    )

    indoor_gauge.add_layout_image(
        dict(
            source=indoor_emoji,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=0.3, sizey=0.3,
            xanchor="center", yanchor="middle"
        )
    )

    indoor_gauge.add_annotation(
        x=arrow_position_offset(indoor_aqi),
        y=-0.02,
        text=indoor_arrow,
        font=dict(size=80, color=indoor_arrow_color),
        showarrow=False
    )

    # Delta annotation for indoor
    indoor_gauge.add_annotation(
        x=arrow_position_offset(indoor_aqi) + 0.05,  # Slightly offset to the right of the arrow
        y=0.12,
        text=indoor_delta_text,
        font=dict(size=30, color=indoor_arrow_color),  # Smaller font for delta
        showarrow=False
    )

    # Outdoor gauge with dynamic number placement
    outdoor_gauge = go.Figure(go.Indicator(
        mode="gauge",
        value=outdoor_aqi,
        gauge={
            'axis': {'range': [0, 150]},
            'bar': {'color': get_gauge_color(outdoor_aqi)},
            'bgcolor': "lightgray",
            'bordercolor': "black",
        }
    ))

    outdoor_gauge.add_annotation(
        x=get_position_offset(outdoor_aqi),
        y=0,
        text=f"<b>{outdoor_aqi}</b>",
        showarrow=False,
        font=dict(size=70, color="black"),
        xanchor="center",
        yanchor="bottom"
    )

    outdoor_gauge.add_layout_image(
        dict(
            source=outdoor_emoji,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=0.3, sizey=0.3,
            xanchor="center", yanchor="middle"
        )
    )

    outdoor_gauge.add_annotation(
        x=arrow_position_offset(outdoor_aqi),
        y=-0.02,
        text=outdoor_arrow,
        font=dict(size=80, color=outdoor_arrow_color),
        showarrow=False
    )

    # Delta annotation for outdoor
    outdoor_gauge.add_annotation(
        x=arrow_position_offset(outdoor_aqi) + 0.05,  # Slightly offset to the right of the arrow
        y=0.12,
        text=outdoor_delta_text,
        font=dict(size=30, color=outdoor_arrow_color),  # Smaller font for delta
        showarrow=False
    )

    return indoor_gauge, outdoor_gauge, indoor_temp_text, outdoor_temp_text



# Helper function to get the last fan state from the database
def get_last_fan_state():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT user_input FROM user_control ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "OFF"  # Default to "OFF" if no data

# Initialize the button text based on the last saved state
@app.callback(
    [Output('disable-fan', 'children'), Output('workflow-state', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def initialize_button_state(n_intervals):
    last_state = get_last_fan_state()
    button_text = "Enable Fan" if last_state == "OFF" else "Override Fan"
    stage = 'fan_off' if last_state == "OFF" else 'initial'
    return button_text, {'stage': stage}

@app.callback(
    [Output('modal-confirm', 'is_open'),
     Output('modal-warning', 'is_open'),
     Output('modal-notification', 'is_open'),
     Output('disable-fan', 'children', allow_duplicate=True),
     Output('disable-fan', 'style'),  # Add style output for dynamic color
     Output('workflow-state', 'data', allow_duplicate=True)],
    [Input('disable-fan', 'n_clicks'),
     Input('confirm-yes', 'n_clicks'),
     Input('confirm-no', 'n_clicks'),
     Input('warning-yes', 'n_clicks'),
     Input('warning-no', 'n_clicks'),
     Input('close-notification', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State('workflow-state', 'data')],
    prevent_initial_call=True
)
def handle_modals(disable_fan_clicks, confirm_yes_clicks, confirm_no_clicks, warning_yes_clicks, warning_no_clicks,
                  close_notification, n_intervals, workflow_state):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0] if callback_context.triggered else None

    # State initialization
    confirm_open = False
    warning_open = False
    notification_open = False

    # Initialize the button state based on the last fan state in the database
    last_state = get_last_fan_state()
    stage = workflow_state.get('stage', 'fan_off' if last_state == "OFF" else 'initial')
    button_text = "Enable Fan" if last_state == "OFF" else "Disable Fan"

    # Define the button style dynamically based on its state
    button_style = {
        "width": "200px",
        "height": "100px",
        "border-radius": "200px",
        "font-size": "1.8rem",
        "color": "white",
        "backgroundColor": "green" if button_text == "Enable Fan" else "red",
        "border": "2px solid green" if button_text == "Enable Fan" else "2px solid red"  # Match border with background color
    }

    # If the `interval-component` triggered this callback, set the initial state without further actions
    if triggered_id == 'interval-component':
        return confirm_open, warning_open, notification_open, button_text, button_style, {'stage': stage}

    # Workflow logic
    if triggered_id == 'disable-fan' and stage == 'initial':
        confirm_open = True
        stage = 'confirm'
    elif triggered_id == 'confirm-yes':
        confirm_open = False
        warning_open = True
        stage = 'warning'
    elif triggered_id == 'warning-yes':
        update_fan_state('OFF')  # Disables the fan
        button_text = "Enable Fan"
        button_style["backgroundColor"] = "green"
        button_style["border"] = "2px solid green"
        stage = 'fan_off'
    elif triggered_id == 'disable-fan' and stage == 'fan_off':
        update_fan_state('ON')  # Re-enables the fan
        button_text = "Override Fan"
        button_style["backgroundColor"] = "red"
        button_style["border"] = "2px solid red"
        stage = 'initial'
        notification_open = True
    elif triggered_id == 'close-notification':
        notification_open = False
    elif triggered_id == 'confirm-no' or triggered_id == 'warning-no':
        stage = 'initial'

    return confirm_open, warning_open, notification_open, button_text, button_style, {'stage': stage}


# New layout function for the second page with the historical graph
def historical_conditions_layout():
    conn = sqlite3.connect(db_path)
    try:
        # Query historical data for indoor and outdoor AQI
        indoor_data = pd.read_sql("SELECT timestamp, pm25 FROM Indoor ORDER BY timestamp DESC LIMIT 500;", conn)
        outdoor_data = pd.read_sql("SELECT timestamp, pm25_value FROM Outdoor ORDER BY timestamp DESC LIMIT 500;", conn)
    except Exception as e:
        print(f"Error retrieving data: {e}")
        indoor_data = pd.DataFrame(columns=["timestamp", "pm25"])
        outdoor_data = pd.DataFrame(columns=["timestamp", "pm25_value"])
    finally:
        conn.close()
    
    # Convert timestamp columns to datetime
    indoor_data['timestamp'] = pd.to_datetime(indoor_data['timestamp'])
    outdoor_data['timestamp'] = pd.to_datetime(outdoor_data['timestamp'])
    
    # Create the graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=indoor_data['timestamp'], y=indoor_data['pm25'], mode='lines', name='Indoor AQI'))
    fig.add_trace(go.Scatter(x=outdoor_data['timestamp'], y=outdoor_data['pm25_value'], mode='lines', name='Outdoor AQI'))
    
    fig.update_layout(
        title="HISTORICAL CONDITIONS",
        xaxis_title="Timestamp",
        yaxis_title="AQI",
        template="plotly_white",
        height=600,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Historical AQI Conditions", className="text-center mb-4"))),
        dbc.Row(dbc.Col(dcc.Graph(figure=fig))),
    ], fluid=True, className="p-4")

def update_fan_state(state):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_control (timestamp, user_input) VALUES (?, ?)', (timestamp, state))
    conn.commit()
    conn.close()

# Layout setup with page navigation
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return dashboard_layout()
    elif pathname == '/historical':
        return historical_conditions_layout()
    else:
        return html.Div("Page not found")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
