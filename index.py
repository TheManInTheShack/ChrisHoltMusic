# ------------------------------------------------------------------------------
# Imports from Dash and the other assets in this group
# ------------------------------------------------------------------------------
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from layouts import layout_splash, layout_performances, layout_shows, layout_songs, layout_albums, layout_artists, layout_people, layout_originals
import callbacks

# ------------------------------------------------------------------------------
# Single-level layout holds the whole page
# ------------------------------------------------------------------------------
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# ------------------------------------------------------------------------------
# Path routing
# ------------------------------------------------------------------------------
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))

def display_page(pathname):
    if pathname == '/':
         return layout_splash
    elif pathname == '/performances':
         return layout_performances
    elif pathname == '/shows':
         return layout_shows
    elif pathname == '/songs':
         return layout_songs
    elif pathname == '/albums':
         return layout_albums
    elif pathname == '/artists':
         return layout_artists
    elif pathname == '/people':
         return layout_people
    elif pathname == '/originals':
         return layout_originals
    else:
        return '404'

# ------------------------------------------------------------------------------
# Run the server
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    print("...starting server...")
    app.run_server(debug=True)
