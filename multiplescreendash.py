import dash
from dash import dcc, html, Input, Output, State
import logging

# Configure logging
logging.basicConfig(filename='screen_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout for the app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='current-screen', storage_type='session'),
    html.Div(id='page-content'),
    html.Div([
        html.Button('<', id='prev-button', n_clicks=0, style={'font-size': '24px', 'height': '50px', 'width': '50px'}),
        html.Button('>', id='next-button', n_clicks=0, style={'font-size': '24px', 'height': '50px', 'width': '50px'})
    ], style={'position': 'fixed', 'top': '50%', 'transform': 'translateY(-50%)', 'width': '100%', 'display': 'flex',
              'justify-content': 'space-between', 'padding': '0 10px'})
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


# Define a callback to update the page content and store the current path
@app.callback(
    [Output('page-content', 'children'),
     Output('current-screen', 'data')],
    [Input('url', 'pathname')]
)
def display_page(pathname):
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


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
