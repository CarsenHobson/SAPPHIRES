import dash
from dash import dcc, html, Input, Output, State
import logging
import RPi.GPIO as GPIO
import time
import threading

# Configure logging
logging.basicConfig(filename='screen_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# GPIO setup for PIR sensor
PIR_PIN = 17  # Replace with your GPIO pin connected to the PIR sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout for the app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='current-screen', storage_type='session'),
    dcc.Store(id='black-screen', data=False, storage_type='session'),
    html.Div(id='page-content'),
    html.Div([
        html.Button('<', id='prev-button', n_clicks=0, style={'font-size': '24px', 'height': '50px', 'width': '50px'}),
        html.Button('>', id='next-button', n_clicks=0, style={'font-size': '24px', 'height': '50px', 'width': '50px'})
    ], style={'position': 'fixed', 'top': '50%', 'transform': 'translateY(-50%)', 'width': '100%', 'display': 'flex',
              'justify-content': 'space-between', 'padding': '0 10px'}),
    dcc.Interval(id='interval-component', interval=1 * 1000, n_intervals=0),  # check every second
    html.Div(id='black-screen-div', style={'display': 'none'})
])

# Define the layout for each page
page_1_layout = html.Div([
    html.H1('Page 1'),
    html.P('Welcome to Page 1')
])

page_2_layout = html.Div([
    html.H1('Page 2'),
    html.P('Welcome to Page 2')
])

page_3_layout = html.Div([
    html.H1('Page 3'),
    html.P('Welcome to Page 3')
])

black_screen_layout = html.Div(style={'height': '100vh', 'backgroundColor': 'black'})


# Define a combined callback to handle both page display and black screen
@app.callback(
    [Output('page-content', 'children'),
     Output('current-screen', 'data')],
    [Input('url', 'pathname'),
     Input('black-screen', 'data')],
    [State('current-screen', 'data')]
)
def display_page(pathname, black_screen_active, current_screen):
    if black_screen_active:
        return black_screen_layout, current_screen
    if pathname == '/page-1':
        return page_1_layout, '/page-1'
    elif pathname == '/page-2':
        return page_2_layout, '/page-2'
    elif pathname == '/page-3':
        return page_3_layout, '/page-3'
    else:
        return page_1_layout, '/page-1'  # default


# Define a callback to update the URL based on button clicks and log the screen change
@app.callback(
    Output('url', 'pathname'),
    [Input('prev-button', 'n_clicks'), Input('next-button', 'n_clicks')],
    [State('url', 'pathname'), State('current-screen', 'data')]
)
def update_url(prev_clicks, next_clicks, current_path, current_screen):
    if current_path is None or current_path == '/':
        current_path = '/page-1'

    page_order = ['/page-1', '/page-2', '/page-3']
    current_index = page_order.index(current_screen or current_path)

    ctx = dash.callback_context
    if not ctx.triggered:
        return current_path
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'prev-button':
        new_index = (current_index - 1) % len(page_order)
    elif button_id == 'next-button':
        new_index = (current_index + 1) % len(page_order)

    new_path = page_order[new_index]
    logging.info(f'Navigated to: {new_path}')
    return new_path


# Combined callback to handle inactivity and user interaction reset
@app.callback(
    [Output('interval-component', 'n_intervals'),
     Output('black-screen', 'data')],
    [Input('interval-component', 'n_intervals'),
     Input('page-content', 'n_clicks'),
     Input('prev-button', 'n_clicks'),
     Input('next-button', 'n_clicks')],
    [State('black-screen', 'data')]
)
def manage_black_screen(n_intervals, page_clicks, prev_clicks, next_clicks, black_screen_active):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'interval-component':
        if not black_screen_active and n_intervals >= 300:  # 5 minutes = 300 seconds
            logging.info('Screen went black due to inactivity')
            return dash.no_update, True
        return dash.no_update, black_screen_active
    else:
        if black_screen_active:
            logging.info('Screen woke up due to user interaction')
        return 0, False


# Function to detect PIR sensor input
def pir_detect():
    while True:
        if GPIO.input(PIR_PIN):
            logging.info('PIR sensor detected movement')
            with app.server.app_context():
                dash.callback_context._callback_list[2]['state'] = (0, False)
                dash.callback_context._callback_list[2]['triggered'][0] = 'interval-component.n_intervals'
        time.sleep(0.1)


# Start the PIR detection thread
pir_thread = threading.Thread(target=pir_detect)
pir_thread.daemon = True
pir_thread.start()


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
