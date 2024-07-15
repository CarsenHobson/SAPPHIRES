import dash
import dash_bootstrap_components as dbc
from dash import html, Input, Output
import sqlite3
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app
app.layout = dbc.Container(
    [
        dbc.Button("Click Me", id="random-button", color="primary"),
        html.Div(id="output"),
    ],
    className="mt-3",
)

# Database setup
DATABASE_PATH = "button_clicks.db"

# Function to initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Define the callback to handle button clicks
@app.callback(
    Output("output", "children"),
    Input("random-button", "n_clicks"),
)
def log_click(n_clicks):
    if n_clicks:
        # Log the click to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        cursor.execute("INSERT INTO clicks (timestamp) VALUES (?)", (timestamp,))
        conn.commit()
        conn.close()
        return f"Button clicked {n_clicks} times"

if __name__ == "__main__":
    app.run_server(debug=True)
