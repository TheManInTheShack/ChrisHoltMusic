# ==================================================================================================
# This control structure is pulled in from the index; it is separated to avoid a circular reference
# ==================================================================================================

# ------------------------------------------------------------------------------
# All we need here is the top level of Dash
# ------------------------------------------------------------------------------
import dash
import dash_bootstrap_components as dbc

# ------------------------------------------------------------------------------
# Overall application
# ------------------------------------------------------------------------------
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP],title="C-Holt's C.H.A.R.T.",update_title="Loading...")

# ------------------------------------------------------------------------------
# Server instance
# ------------------------------------------------------------------------------
server = app.server
