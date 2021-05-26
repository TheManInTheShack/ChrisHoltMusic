# ==================================================================================================
# xxx page
# ==================================================================================================

# ==================================================================================================
# Imports
# ==================================================================================================
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import plotly.express as px

from app import app

from lib import *

# ==================================================================================================
# Init
# ==================================================================================================
print("...loading xxx page...")

def layout_xxx(init_dict):
    # ==============================================================================================
    # Grab the information from the init
    # ==============================================================================================
    style_default      = init_dict['style_default']    
    data               = init_dict['data']                         
    pages              = init_dict['pages']
    footnote           = init_dict['footnote']
    title              = init_dict['title']

    # ==============================================================================================
    # Sort out the data
    # ==============================================================================================

    # ==============================================================================================
    # Page Contents Configuration
    # ==============================================================================================
    # ------------------------------------------------------------------------------
    # Chart information
    #charts['labor_pct']        = {'chart_type':'bar', 'idx':'chart_labor_pct_bar', 'details':{'data':dpt_mean,'x':'practice','y':['ips_derived_labor_pct'], 'style':style_default}}
    #charts['labor_pct_line']   = {'chart_type':'line', 'idx':'chart_labor_pct_line', 'details':{'data':date_mean,'x':'aggr','y':['ips_derived_labor_pct'], 'style':style_default}}
    # ------------------------------------------------------------------------------
    charts={}

    # ------------------------------------------------------------------------------
    # Control information
    #bu_opt = [{'label':i,'value':i} for i in list_all_depts]
    #time_opt = [{'label':i,'value':i} for i in ddata['year'].to_list()]
    #controls['business_unit']      = {'control_type':'dropdown', 'idx':'ctl_bu'        , 'details':{'options':bu_opt       , 'multi':True     ,'value':[]    ,'style':style_default   ,'title':'business_unit'}}
    #controls['time_granularity']   = {'control_type':'dropdown', 'idx':'ctl_timegran'  , 'details':{'options':time_opt       , 'multi':True     ,'value':[]    ,'style':style_default   ,'title':'time_granularity'}}
    #controls['refresh']            = {'control_type':'button'  , 'idx':'ctl_refresh'   , 'details':{'label':"Refresh"  , 'title':'refresh'}}
    # ------------------------------------------------------------------------------
    controls={}

    # ------------------------------------------------------------------------------
    # General layout information
    # ------------------------------------------------------------------------------
    layout={}
    layout['chart_shape']     = "1x2"
    layout['style_default']   = style_default
    layout['controls_orient'] = "top"

    # ==============================================================================================
    # Component layout
    # ==============================================================================================
    # ------------------------------------------------------------------------------
    # Compile components
    # ------------------------------------------------------------------------------
    components = []
    components.append(get_navbar(pages, title))
    components.append(html.P("Hello xxx", style=style_default))
    #components.append(charts_with_controls(charts, controls, layout))
    components.append(get_footnote(footnote))

    # ------------------------------------------------------------------------------
    # Top Level
    # ------------------------------------------------------------------------------
    layout_xxx = html.Div(components, style=style_default)
    return layout_xxx

    # ==============================================================================================
    # Callbacks
    # ==============================================================================================

