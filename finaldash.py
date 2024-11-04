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
db_path = '/home/mainhubs/pm25_data.db'  # Replace with the correct path to your database
DATABASE_PATH = 'fan_state.db'

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
    pm25 REAL
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

CREATE TABLE IF NOT EXISTS pm25_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    pm25_value REAL
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
                    html.Div([
                        # Temperature box in the bottom left
                        html.Div("Temperature", className="d-flex justify-content-center align-items-center",
                                 style={
                                     "width": "400px",
                                     "height": "150px",
                                     "border": "2px solid black",
                                     "position": "absolute",  # Align to the right
                                     "font-size": "1.5rem",
                                     "bottom": "0",
                                     "left": "0",
                                     "text-align": "center",
                                     "background-color": "#D2B48C",
                                     "border-radius": "5px 7px 5px 0"
                                 })
                    ], style={
                        "padding": "30px",
                        "border-left": "2px solid black",
                        "border-right": "2px solid black",
                        "border-bottom": "2px solid black",  # Add a bottom border to align with button
                        "height": "227px",  # Adjust height for bottom third
                        "background-color": "transparent"  # Ensure background is transparent
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
                        # Temperature box in the bottom right
                        html.Div("Temperature", className="d-flex justify-content-center align-items-center",
                                 style={
                                     "width": "400px",
                                     "height": "150px",
                                     "border": "2px solid black",
                                     "position": "absolute",  # Align to the right
                                     "font-size": "1.5rem",
                                     "bottom": "0",
                                     "right": "0",
                                     "text-align": "center",
                                     "background-color": "#7BC8F6",
                                     "border-radius": "7px 5px 5px 0"
                                 })
                    ], style={
                        "padding": "30px",
                        "border-left": "2px solid black",
                        "border-right": "2px solid black",
                        "border-bottom": "2px solid black",  # Add a bottom border to align with button
                        "height": "227px",  # Adjust height for bottom third
                        "background-color": "transparent"  # Ensure background is transparent
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
            dbc.ModalBody("The fan has been re-enabled."),
            dbc.ModalFooter(dbc.Button("Close", id="close-notification", className="btn btn-secondary"))
        ], id="modal-notification", is_open=False, backdrop="static", centered=True),

        dcc.Interval(id='interval-component', interval=10 * 1000, n_intervals=0),
        dcc.Store(id='workflow-state', data={'stage': 'initial'})
    ], fluid=True, className="p-4")


@app.callback(
    [Output('indoor-gauge', 'figure'),
     Output('outdoor-gauge', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    conn = sqlite3.connect(db_path)
    
    # Queries for AQI
    try:
        # Fetch the latest and past 3 indoor AQI readings
        indoor_data = pd.read_sql("SELECT pm25 FROM Indoor ORDER BY timestamp DESC LIMIT 4;", conn)
        outdoor_data = pd.read_sql("SELECT pm25_value FROM pm25_data ORDER BY timestamp DESC LIMIT 4;", conn)
        
        # Determine current AQI values
        indoor_aqi = int(indoor_data['pm25'].iloc[0])
        outdoor_aqi = int(outdoor_data['pm25_value'].iloc[0])

        # Calculate past averages (last 3 readings) for comparison
        indoor_aqi_avg = indoor_data['pm25'].iloc[1:].mean()
        outdoor_aqi_avg = outdoor_data['pm25_value'].iloc[1:].mean()
    except Exception as e:
        print(f"Error retrieving data: {e}")
        indoor_aqi, outdoor_aqi, indoor_aqi_avg, outdoor_aqi_avg = 0, 0, 0, 0
    finally:
        conn.close()

    # Determine arrow direction and color
    indoor_arrow = "⬆️" if indoor_aqi > indoor_aqi_avg else "⬇️"
    indoor_arrow_color = "green" if indoor_aqi < indoor_aqi_avg else "red"

    outdoor_arrow = "⬆️" if outdoor_aqi > outdoor_aqi_avg else "⬇️"
    outdoor_arrow_color = "green" if outdoor_aqi < outdoor_aqi_avg else "red"
    
     # Get emojis
    indoor_emoji = get_aqi_emoji(indoor_aqi)
    outdoor_emoji = get_aqi_emoji(outdoor_aqi)

    # Gauge figures with AQI number and separate arrow annotation
    indoor_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=indoor_aqi,
        gauge={
            'axis': {'range': [0, 150]},
            'bar': {'color': get_gauge_color(indoor_aqi)},
            'bgcolor': "lightgray",
            'bordercolor': "black",
        },
        number={
            "font": {'color': "black"},  # Keep AQI number color standard
            'xanchor': "center",  # Horizontal alignment (options: "auto", "left", "center", "right")
            'yanchor': "bottom",  # Vertical alignment (options: "auto", "top", "middle", "bottom")
            'x': 0.5,  # X-coordinate (relative position from 0 to 1)
            'y': 1.2   # Y-coordinate (relative position, can be adjusted)  # Keep AQI number color standard
        }
    ))
    
   # Add Emoji as an Image for Indoor AQI
    indoor_gauge.add_layout_image(
        dict(
            source=indoor_emoji,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=0.3, sizey=0.3,
            xanchor="center", yanchor="middle"
        )
    )
    # Add arrow as a separate annotation
    indoor_gauge.add_annotation(
        x=0.70, y=-0.02, text=indoor_arrow,
        font=dict(size=80, color=indoor_arrow_color),
        showarrow=False
    )

    outdoor_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=outdoor_aqi,
        gauge={
            'axis': {'range': [0, 150]},
            'bar': {'color': get_gauge_color(outdoor_aqi)},
            'bgcolor': "lightgray",
            'bordercolor': "black",
        },
        number={
            'font': {'color': "black"}  # Keep AQI number color standard
        }
    ))
    # Add Emoji as an Image for Outdoor AQI
    outdoor_gauge.add_layout_image(
        dict(
            source=outdoor_emoji,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=0.3, sizey=0.3,
            xanchor="center", yanchor="middle"
        )
    )
    # Add arrow as a separate annotation
    outdoor_gauge.add_annotation(
        x=0.70, y=-0.02, text=outdoor_arrow,
        font=dict(size=80, color=outdoor_arrow_color),
        showarrow=False
    )

    return indoor_gauge, outdoor_gauge



# Modal workflow callback
@app.callback(
    [Output('modal-confirm', 'is_open'),
     Output('modal-warning', 'is_open'),
     Output('modal-notification', 'is_open'),
     Output('disable-fan', 'children'),
     Output('workflow-state', 'data')],
    [Input('disable-fan', 'n_clicks'),
     Input('confirm-yes', 'n_clicks'),
     Input('confirm-no', 'n_clicks'),
     Input('warning-yes', 'n_clicks'),
     Input('warning-no', 'n_clicks'),
     Input('close-notification', 'n_clicks')],
    [State('workflow-state', 'data')]
)
def handle_modals(disable_fan_clicks, confirm_yes_clicks, confirm_no_clicks, warning_yes_clicks, warning_no_clicks,
                  close_notification, workflow_state):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0] if callback_context.triggered else None

    # State initialization
    confirm_open = False
    warning_open = False
    notification_open = False

    stage = workflow_state.get('stage', 'initial')
    button_text = "Override Fan" if stage == 'initial' else "Enable Fan"

    # Workflow logic
    if triggered_id == 'disable-fan' and stage == 'initial':
        confirm_open = True
        stage = 'confirm'
    elif triggered_id == 'confirm-yes':
        confirm_open = False
        warning_open = True
        stage = 'warning'
    elif triggered_id == 'warning-yes':
        update_fan_state('OFF')
        button_text = "Enable Fan"
        stage = 'fan_off'
    elif triggered_id == 'close-notification':
        notification_open = False
    elif triggered_id == 'confirm-no' or triggered_id == 'warning-no':
        stage = 'initial'

    return confirm_open, warning_open, notification_open, button_text, {'stage': stage}

# Helper functions for fan state
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

# New layout function for the second page with the historical graph
def historical_conditions_layout():
    conn = sqlite3.connect(db_path)
    try:
        # Query historical data for indoor and outdoor AQI
        indoor_data = pd.read_sql("SELECT timestamp, pm25 FROM Indoor ORDER BY timestamp DESC LIMIT 500;", conn)
        outdoor_data = pd.read_sql("SELECT timestamp, pm25_value FROM pm25_data ORDER BY timestamp DESC LIMIT 500;", conn)
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
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO fan_state (state, timestamp) VALUES (?, ?)', (state, timestamp))
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


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
