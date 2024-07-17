import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import os
import logging

# Configure logging
logging.basicConfig(filename='screen_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Path to the image directory
image_directory = '/Users/carsenhobson/Downloads'  # Replace with your image directory
image_filename = 'pic.jpeg'  # Replace with your image filename

# Full path to the image
image_path = os.path.join(image_directory, image_filename)

# Copy the image to the assets folder for Dash to serve it
os.makedirs('assets', exist_ok=True)
if not os.path.exists(os.path.join('assets', image_filename)):
    with open(image_path, 'rb') as src_file:
        with open(os.path.join('assets', image_filename), 'wb') as dest_file:
            dest_file.write(src_file.read())

# Define the layout for the app
app.layout = dbc.Container(
    [
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='current-screen', storage_type='session'),
        dcc.Store(id='black-screen', data=False, storage_type='session'),
        html.Div(id='page-content'),
        dbc.Row(
            dbc.Col(
                html.Button('<', id='prev-button', n_clicks=0,
                            style={'font-size': '24px', 'height': '50px', 'width': '50px'}),
                width='auto',
                className="d-flex justify-content-center align-items-center"
            ),
            style={'position': 'fixed', 'top': '50%', 'left': '0', 'transform': 'translateY(-50%)'}
        ),
        dbc.Row(
            dbc.Col(
                html.Button('>', id='next-button', n_clicks=0,
                            style={'font-size': '24px', 'height': '50px', 'width': '50px'}),
                width='auto',
                className="d-flex justify-content-center align-items-center"
            ),
            style={'position': 'fixed', 'top': '50%', 'right': '0', 'transform': 'translateY(-50%)'}
        ),
        dcc.Interval(id='interval-component', interval=1 * 1000, n_intervals=0)  # check every second
    ],
    fluid=True
)

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

# Use local image for screen saver
screen_saver_layout = html.Div([
    html.Img(src=f'/assets/{image_filename}', style={'width': '100%', 'height': '100vh', 'object-fit': 'cover'})
])


# Define a combined callback to handle both page display and screen saver
@app.callback(
    [Output('page-content', 'children'),
     Output('current-screen', 'data')],
    [Input('url', 'pathname'),
     Input('black-screen', 'data')],
    [State('current-screen', 'data')]
)
def display_page(pathname, black_screen_active, current_screen):
    if black_screen_active:
        return screen_saver_layout, current_screen
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
        if not black_screen_active and n_intervals >= 30:  # 5 minutes = 300 seconds
            logging.info('Screen went to image due to inactivity')
            return dash.no_update, True
        return dash.no_update, black_screen_active
    else:
        if black_screen_active:
            logging.info('Screen woke up due to user interaction')
        return 0, False


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
