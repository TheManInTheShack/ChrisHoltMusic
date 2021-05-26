# ==================================================================================================
# INDEX
# This file runs the overall dashboard program
# - Includes the other pieces as imports
# - Puts together the multi-page index and routing
# - Runs the server
# ==================================================================================================

# ==================================================================================================
# Imports from Dash and the other assets in this group
# ==================================================================================================
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

from page_splash import *
from page_performances import *
from page_shows import *
from page_songs import *
from page_albums import *
from page_artists import *
from page_people import *
from page_originals import *
from initialize import init_dict

# ==================================================================================================
# Info about the navigable pages
# ==================================================================================================
pages = {}
pages['splash']        = {'href':"/"             , 'name':"Home"            , 'func':layout_splash          }
pages['performances']  = {'href':"/performances" , 'name':"Performances"    , 'func':layout_performances    }
pages['shows']         = {'href':"/shows"        , 'name':"Shows"           , 'func':layout_shows           }
pages['songs']         = {'href':"/songs"        , 'name':"Songs"           , 'func':layout_songs           }
pages['albums']        = {'href':"/albums"       , 'name':"Albums"          , 'func':layout_albums          }
pages['artists']       = {'href':"/artists"      , 'name':"Artists"         , 'func':layout_artists         }
pages['people']        = {'href':"/people"       , 'name':"People"          , 'func':layout_people          }
pages['originals']     = {'href':"/originals"    , 'name':"Originals"       , 'func':layout_originals       }

# ------------------------------------------------------------------------------
# Store into the dict to be pushed into the layout
# ------------------------------------------------------------------------------
init_dict['pages'] = pages

# ==================================================================================================
# Put together the multi-page index and routing
# ==================================================================================================
# ------------------------------------------------------------------------------
# Single-level layout holds the whole page
# ------------------------------------------------------------------------------
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
], fluid=True)

# ------------------------------------------------------------------------------
# Path routing via a special callback
# - The output is the Div that we made just above
# - The input is the url typed into the browser
# - Each formal path ending will have a corresponding function in layouts
# ------------------------------------------------------------------------------
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    for page in pages:
        if pathname == pages[page]['href']:
            out = pages[page]['func'](init_dict)
            return out
    return '404'

# ==================================================================================================
# Run the server
# ==================================================================================================
# ------------------------------------------------------------------------------
# if in production mode we need to have a reference to the server for wsgi
# ------------------------------------------------------------------------------
server = app.server

# ------------------------------------------------------------------------------
# If we are running it in test mode
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    print("...starting server...")
    app.run_server(debug=True)
