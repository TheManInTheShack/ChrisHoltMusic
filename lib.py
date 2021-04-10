
# ==================================================================================================
# Imports
# ==================================================================================================
import pandas as pd
import plotly.express as px
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input

# ==================================================================================================
# FUNCTIONS FOR GENERATING AND DISPLAYING TABLES
# ==================================================================================================

# ------------------------------------------------------------------------------
# This is the generic code to generate a table from any dataframe; this is
# the simple bootstrap table, only suitable for small outputs
# ------------------------------------------------------------------------------
def generate_simple_table(data, idx, max_rows=50):
    # --------------------------------------------------------------------------
    # The table object
    # --------------------------------------------------------------------------
    head = html.Thead(html.Tr([html.Th(col) for col in data.columns]))
    body = html.Tbody([ html.Tr([html.Td(data.iloc[i][col]) for col in data.columns]) for i in range(min(len(data), max_rows)) ])
    table = dbc.Table([head, body],id=idx,bordered=True,dark=True,hover=True,responsive=True,striped=True,size='sm',style={'overflowY':'scroll'})

    # --------------------------------------------------------------------------
    # Consolidate
    # --------------------------------------------------------------------------
    components = []
    components.append(get_empty_col())
    components.append(html.Div(table, className = 'col-10'))
    components.append(get_empty_col())

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return html.Div(components, className = 'row')

# ------------------------------------------------------------------------------
# Bundle the components used to display a simple table
# ------------------------------------------------------------------------------
def display_simple_table(df, idx="", title=""):
    components = []

    components.append(get_emptyrow())
    components.append(html.H3(title))
    components.append(generate_simple_table(df, idx))

    return components

# ------------------------------------------------------------------------------
# This is for 'real' tables
# ------------------------------------------------------------------------------
def generate_data_table(df, idx, height='500px'):
    # --------------------------------------------------------------------------
    # The table object
    # --------------------------------------------------------------------------
    table = dash_table.DataTable(
            id=idx,
            data = df.to_dict('records'),
            columns = [{'id':c, 'name':c} for c in df.columns],
            filter_action='native',
            page_action='none',
            #fixed_rows={'headers':True},    <------TODO WHEN THIS IS ON, THE FILTERS SHOW NOTHING
            style_cell={'whiteSpace':'normal','height':'auto','textAlign':'left', 'minWidth':'50px', 'maxWidth':'180px'},
            style_table={'height':height, 'overflowY':'auto' },
            style_header={'backgroundColor':'Black', 'fontWeight':'bold', 'textAlign':'center' },
            style_data_conditional=[{'if': {'row_index':'odd'},'backgroundColor':'rgb(0,0,0)'},{'if': {'row_index':'even'},'backgroundColor':'rgb(25,25,25)'}],
            style_as_list_view=False,
            sort_action='native',
            sort_mode='multi'
            )

    # --------------------------------------------------------------------------
    # Consolidate
    # --------------------------------------------------------------------------
    components = []
    components.append(get_empty_col())
    components.append(html.Div(table, className = 'col-10'))
    components.append(get_empty_col())

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return html.Div(components, className = 'row')

# ------------------------------------------------------------------------------
# Bundle the components used to display a data table
# ------------------------------------------------------------------------------
def display_data_table(df, idx="", title="", height="500px"):
    components = []

    components.append(get_emptyrow())
    components.append(html.H3(title))
    components.append(generate_data_table(df, idx, height))

    return components

# ==================================================================================================
# FUNCTIONS FOR GENERATING AND DISPLAYING CHARTS
# ==================================================================================================

# ------------------------------------------------------------------------------
# Display one or more charts on the page as rows
# ------------------------------------------------------------------------------
def display_chart(shape, charts, title):
    # --------------------------------------------------------------------------
    # Depending on the shape this will happen differently
    # Start with the simple single chart
    # --------------------------------------------------------------------------
    if shape=="1x1":
        # ----------------------------------------------------------------------
        # Make it a row with a margin of 1/12
        # ----------------------------------------------------------------------
        row_components = []
        row_components.append(get_empty_col())
        row_components.append(html.Div(charts[0], className = 'col-10'))
        row_components.append(get_empty_col())

        row = html.Div(row_components, className = 'row')

        # ----------------------------------------------------------------------
        # Put everything together
        # ----------------------------------------------------------------------
        components = []
        components.append(get_emptyrow())
        components.append(html.H3(title))
        components.append(row)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return components

# ------------------------------------------------------------------------------
# Make a bar chart
# ------------------------------------------------------------------------------
def generate_bar(data, idx, x, y, color="", style={}, config={}):
    # --------------------------------------------------------------------------
    # Make the bar chart figure
    # --------------------------------------------------------------------------
    if color:
        bar = px.bar(data, x=x, y=y, barmode='group', color=color)
    else:
        bar = px.bar(data, x=x, y=y, barmode='group')

    # --------------------------------------------------------------------------
    # Update styling
    # --------------------------------------------------------------------------
    if 'backgroundColor' in style:
        bar.update_layout(plot_bgcolor=style['backgroundColor'])
        bar.update_layout(paper_bgcolor=style['backgroundColor'])
    if 'color' in style:
        bar.update_layout(font_color=style['color'])

    # --------------------------------------------------------------------------
    # Make the chart 
    # --------------------------------------------------------------------------
    chart = dcc.Graph(id=idx, figure=bar)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return chart





# ==================================================================================================
# FUNCTIONS FOR RETRIEVING/BUILDING GENERAL AND SPECIFIC DATA FRAMES
# ==================================================================================================

# ------------------------------------------------------------------------------
# Prepare the performance-based data
# ------------------------------------------------------------------------------
def get_data_performances(data):
    # --------------------------------------------------------------------------
    # Start with the performances
    # --------------------------------------------------------------------------
    sdata = data['Performances'][['Series Index','Set Position','Song','Artist']]
    sdata = sdata.rename(columns={'Series Index':'Show', 'Set Position':'Position'})

    # --------------------------------------------------------------------------
    # Add the year and the composers from the song Table
    # --------------------------------------------------------------------------
    songdata = data['Songs'][['Album','Year','Composer']]
    sdata = sdata.merge(songdata, how='left', left_on=['Song','Artist'], right_on=['Name','Band'])

    # --------------------------------------------------------------------------
    # Add the 'family' of artists
    # --------------------------------------------------------------------------
    family = data['Bands'][['Band Family']]
    sdata =sdata.merge(family, how='left', left_on=['Artist'], right_on=['Name'])
    sdata = sdata.rename(columns={'Band Family':'Family'})

    # --------------------------------------------------------------------------
    # Calculate the number of times played
    # --------------------------------------------------------------------------
    numtimes = data['Performances'][['Song','Artist']].reset_index(drop=True)
    numtimes['Times Played'] = 1
    numtimes = numtimes.groupby(['Song','Artist']).sum()

    sdata = sdata.merge(numtimes, how='left', on=['Song','Artist'])

    # --------------------------------------------------------------------------
    # Flag as CH original or not
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return sdata

# ------------------------------------------------------------------------------
# Prepare the Show-based data
# ------------------------------------------------------------------------------
def get_data_shows(data):
    # --------------------------------------------------------------------------
    # Start with the shows
    # --------------------------------------------------------------------------
    sdata = data['Gigs'][['Location','Date/Time Start','Show Title']]

    # --------------------------------------------------------------------------
    # Get the number of songs played
    # --------------------------------------------------------------------------
    numsongs = data['Performances'][['Series Index']].reset_index(drop=True)
    numsongs['Count'] = 1
    numsongs = numsongs.groupby('Series Index').sum()

    sdata = sdata.merge(numsongs, how='left', left_on=['Series Index'], right_on=['Series Index'])

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return sdata

# ------------------------------------------------------------------------------
# Prepare the Song-based data
# ------------------------------------------------------------------------------
def get_data_songs(data):
    # --------------------------------------------------------------------------
    # Start with the songs
    # --------------------------------------------------------------------------
    sdata = data['Songs'][['Name','Band','Album','Year','Genre','Composer','Covered']].reset_index(drop=True)
    sdata = sdata.rename(columns={'Name':'Song', 'Band':'Artist'})

    # --------------------------------------------------------------------------
    # Get the number of times played
    # --------------------------------------------------------------------------
    numtimes = data['Performances'][['Song','Artist']].reset_index(drop=True)
    numtimes['Times Played'] = 1
    numtimes = numtimes.groupby(['Song','Artist']).sum()

    sdata = sdata.merge(numtimes, how='left', on=['Song','Artist'])

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return sdata


# ------------------------------------------------------------------------------
# Prepare the Album-based data
# ------------------------------------------------------------------------------
def get_data_albums(data):
    # --------------------------------------------------------------------------
    # Start with the Albums
    # --------------------------------------------------------------------------
    sdata = data['Albums'][['Name','Band','Personnel']].reset_index(drop=True)
    sdata = sdata.rename(columns={'Name':'Album','Band':'Artist'})

    # --------------------------------------------------------------------------
    # TODO Can we get the track listing for each album?
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # TODO derive a list of the songs that have been played from each album
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # TODO Fields for total # of songs and # of songs played
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return sdata

# ------------------------------------------------------------------------------
# Prepare the Artist-based data
# ------------------------------------------------------------------------------
def get_data_artists(data):
    # --------------------------------------------------------------------------
    # Start with the Artists
    # --------------------------------------------------------------------------
    sdata = data['Bands'][['Name','Genres','Chris Relationship','Band Family','Band Birthplace']].reset_index(drop=True)
    sdata = sdata.rename(columns={'Name':'Artist','Chris Relationship':'CH Relation'})

    # --------------------------------------------------------------------------
    # TODO Get number of times played from performances
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return sdata

# ------------------------------------------------------------------------------
# Prepare the People-based data
# ------------------------------------------------------------------------------
def get_data_people(data):
    # --------------------------------------------------------------------------
    # Start with the People
    # --------------------------------------------------------------------------
    sdata = data['People'][['Name','Year Born','Year Died','Instruments','Bands','Notes','AllMusic','Wikipedia']].reset_index(drop=True)
    sdata = sdata.rename(columns={'Name':'Person'})

    # --------------------------------------------------------------------------
    # TODO Get number of times referenced?
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return sdata

# ------------------------------------------------------------------------------
# Prepare the Originals-based data
# ------------------------------------------------------------------------------
def get_data_originals(data):
    # --------------------------------------------------------------------------
    # Start with the Songs
    # --------------------------------------------------------------------------
    sdata = data['Songs'][['Name','Band','Album','Year','Genre','Composer','Covered']].reset_index(drop=True)
    sdata = sdata.rename(columns={'Name':'Song', 'Band':'Artist'})
    sdata = sdata[sdata['Composer'] == 'Chris Holt']

    # --------------------------------------------------------------------------
    # TODO Get number of times played
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return sdata

# ------------------------------------------------------------------------------
# Get data needed for specific chart
# Number of different songs played by artist (with minimum)
# ------------------------------------------------------------------------------
def get_data_num_songs_by_artist(data, minsongs=0):
    # --------------------------------------------------------------------------
    # Get the whole count
    # --------------------------------------------------------------------------
    count = data['Songs']['Band'].value_counts(sort=True, ascending=False)

    # --------------------------------------------------------------------------
    # Reset the minimum if requested
    # --------------------------------------------------------------------------
    if minsongs > 0:
        count = count.loc[count >= minsongs]

    # --------------------------------------------------------------------------
    # Make the count into a dataframe and label the columns
    # --------------------------------------------------------------------------
    sdata = pd.DataFrame(list(zip(count.index.tolist(), count.tolist())), columns=["Originating Artist","Number of Songs Played"])

    # --------------------------------------------------------------------------
    # Add a column to say whether the band is one of Chris's originals
    # --------------------------------------------------------------------------
    sdata['CH Original'] = sdata['Originating Artist']
    sdata['CH Original'] = sdata['CH Original'].apply(band_is_original, args=([data['Bands']]))

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return sdata

# ------------------------------------------------------------------------------
# Get data needed for specific chart
# Number of different songs played by year
# ------------------------------------------------------------------------------
def get_data_num_songs_by_year(data):
    # ----------------------------------------------------------------------
    # Get the whole count
    # ----------------------------------------------------------------------
    count = data['Songs']['Year'].value_counts(sort=True, ascending=False)

    # ----------------------------------------------------------------------
    # Make the count into a dataframe and label the columns
    # ----------------------------------------------------------------------
    sdata = pd.DataFrame(list(zip(count.index.tolist(), count.tolist())), columns=["Year of Song's Origination","Number of Songs Played"])

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return sdata

# ------------------------------------------------------------------------------
# Return Yes/No for whether the band is one of Chris's originals...takes
# in the band and the lookup table
# ------------------------------------------------------------------------------
def band_is_original(band, band_data):
    # --------------------------------------------------------------------------
    # Maybe there's a mismatch in the data
    # --------------------------------------------------------------------------
    if not band in band_data.index:
        print("WARNING! Name not found in data['band']: " + band)
        return "No"
    # --------------------------------------------------------------------------
    # Or maybe we can look it up
    # --------------------------------------------------------------------------
    else:
        this_one = band_data['Chris Relationship'].loc[band]
        if this_one == "Original":
            return "Yes"
        else:
            return "No"

# ==================================================================================================
# BUILD WHOLE-PAGE COMPONENTS - HEADER, NAVIGATION, FOOTNOTE
# ==================================================================================================

# ------------------------------------------------------------------------------
# Header with logo
# ------------------------------------------------------------------------------
def get_header(app, title, logo):
    # --------------------------------------------------------------------------
    # Left is an empty space
    # --------------------------------------------------------------------------
    left = html.Div([], className = 'col-2')

    # --------------------------------------------------------------------------
    # Center is the title
    # --------------------------------------------------------------------------
    center = html.Div([
            html.H1(children=title,
                    style = {'textAlign' : 'center'}
            )],
            className = 'col-8',
            style = {'padding-top' : '1%'}
        )

    # --------------------------------------------------------------------------
    # Right is the logo
    # --------------------------------------------------------------------------
    right = html.Div([
            html.Img(
                    src = app.get_asset_url(logo),
                    height = '43 px',
                    width = 'auto')
            ],
            className = 'col-2',
            style = {
                    'align-items': 'center',
                    'padding-top' : '1%',
                    'height' : 'auto'})

    # --------------------------------------------------------------------------
    # Final product is all three put together as a single 'row'
    # --------------------------------------------------------------------------
    header = html.Div([left, center, right], className = 'row', style = {'height' : '4%'})

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return header


# ------------------------------------------------------------------------------
# Nav bar
# pages['splash']        = {'href':"/"                 , 'name':"Home"         }
# ------------------------------------------------------------------------------
def get_navbar(pages, current_page):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    components = []

    # --------------------------------------------------------------------------
    # Special styling for the navbar piece
    # --------------------------------------------------------------------------
    navbarcurrentpage = {
    'text-decoration' : 'underline',
    'text-shadow': '0px 0px 1px rgb(251, 251, 252)'
    }

    # --------------------------------------------------------------------------
    # Left side hsa a blank column
    # --------------------------------------------------------------------------
    components.append(html.Div([], className = 'col-2'))

    # --------------------------------------------------------------------------
    # One item for each page
    # --------------------------------------------------------------------------
    for page in pages:
        # ----------------------------------------------------------------------
        # Maybe this is the current page, it has extra styling
        # ----------------------------------------------------------------------
        if page == current_page:
            components.append(html.Div([ dcc.Link( html.H4(children = pages[page]['name'], style = navbarcurrentpage), href=pages[page]['href']) ], className = 'col-1'))

        # ----------------------------------------------------------------------
        # Or maybe it's one of the other pages
        # ----------------------------------------------------------------------
        else:
            components.append(html.Div([ dcc.Link( html.H4(children = pages[page]['name']), href=pages[page]['href']) ], className = 'col-1'))

    # --------------------------------------------------------------------------
    # Margin on the right with whatever is left over
    # --------------------------------------------------------------------------
    right_width = 12-len(pages)-1
    coltype = 'col-' + str(right_width)
    components.append(html.Div([], className = coltype))

    # --------------------------------------------------------------------------
    # Make the whole navbar
    # --------------------------------------------------------------------------
    navbar = html.Div(components, className = 'row')

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return navbar

# ------------------------------------------------------------------------------
# Empty row
# This returns an empty row of a defined height
# ------------------------------------------------------------------------------
def get_emptyrow(h='45px'):
    emptyrow = html.Div([
        html.Div([
            html.Br()
        ], className = 'col-12')
    ],
    className = 'row',
    style = {'height' : h})

    return emptyrow

# ------------------------------------------------------------------------------
# Empty column
# ------------------------------------------------------------------------------
def get_empty_col():
    empty_col = html.Div([], className = 'col-1')
    return empty_col

# ------------------------------------------------------------------------------
# Footnote has the credits and the rev#
# ------------------------------------------------------------------------------
def get_footnote(footnote):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    components = []

    # --------------------------------------------------------------------------
    # Parts
    # --------------------------------------------------------------------------
    components.append(get_emptyrow())
    components.append(html.P(footnote['credits']))
    components.append(html.P(footnote['revnum']))

    # --------------------------------------------------------------------------
    # Consolidate
    # --------------------------------------------------------------------------
    fnote = html.Div(components, style={'font-size':'small'})

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return fnote

# ==================================================================================================
# BUILD OTHER SPECIFIC BUT COMPLEX PIECES
# ==================================================================================================

# ------------------------------------------------------------------------------
# Splash page
# ------------------------------------------------------------------------------
def make_splash_page(app, image, blurbs):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    components = []
    row = []

    # --------------------------------------------------------------------------
    # Make an empty column to use in the layout
    # --------------------------------------------------------------------------
    empty_col = html.Div([], className = 'col-1')

    # --------------------------------------------------------------------------
    # Get the image
    # --------------------------------------------------------------------------
    image = html.Div([ html.Img( src = app.get_asset_url(image)) ],
            className = 'col-5',
            style = { 'align-items': 'center', 'padding-top' : '1%'})

    # --------------------------------------------------------------------------
    # Parts
    # --------------------------------------------------------------------------
    blob = []
    for blurb in blurbs:
        blob.append(html.P(blurb))

    text_block = html.Div(blob, className = 'col-5')


    # --------------------------------------------------------------------------
    # Consolidate
    # --------------------------------------------------------------------------
    row = html.Div([empty_col, image, text_block, empty_col], className = 'row')

    splash = html.Div([get_emptyrow(), row])

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return splash


# ==================================================================================================
# OBSELETE
# ==================================================================================================
# ------------------------------------------------------------------------------
#### Function to produce charts from the data
#### ------------------------------------------------------------------------------
###def get_chart(data, selection, config = {}):
###    # --------------------------------------------------------------------------
###    # Number of different songs played by artist (with minimum)
###    # --------------------------------------------------------------------------
###    if selection=="number_of_songs_by_artist":
###        # ----------------------------------------------------------------------
###        # Get the whole count
###        # ----------------------------------------------------------------------
###        count = data['Songs']['Band'].value_counts(sort=True, ascending=False)
###
###        # ----------------------------------------------------------------------
###        # Reset the minimum if requested
###        # ----------------------------------------------------------------------
###        if 'min' in config:
###            count = count.loc[count >= config['min']]
###
###        # ----------------------------------------------------------------------
###        # Make the count into a dataframe and label the columns
###        # ----------------------------------------------------------------------
###        df = pd.DataFrame(list(zip(count.index.tolist(), count.tolist())), columns=["Originating Artist","Number of Songs Played"])
###
###        # ----------------------------------------------------------------------
###        # Add a column to say whether the band is one of Chris's originals
###        # ----------------------------------------------------------------------
###        df['CH Original'] = df['Originating Artist']
###        df['CH Original'] = df['CH Original'].apply(band_is_original, args=([data['Bands']]))
###
###        # ----------------------------------------------------------------------
###        # Make it into a bar chart
###        # ----------------------------------------------------------------------
###        bar = px.bar(df, x='Originating Artist', y='Number of Songs Played', color='CH Original', barmode='group')
###
###        # ----------------------------------------------------------------------
###        # Update the design based on the config
###        # ----------------------------------------------------------------------
###        if 'style' in config: 
###            if 'backgroundColor' in config['style']:
###                bar.update_layout(plot_bgcolor=config['style']['backgroundColor'])
###                bar.update_layout(paper_bgcolor=config['style']['backgroundColor'])
###            if 'color' in config['style']:
###                bar.update_layout(font_color=config['style']['color'])
###
###        # ----------------------------------------------------------------------
###        # Send back the chart
###        # ----------------------------------------------------------------------
###        return bar
###
###    # --------------------------------------------------------------------------
###    # Number of different songs played by year
###    # --------------------------------------------------------------------------
###    if selection=="number_of_songs_by_year":
###        # ----------------------------------------------------------------------
###        # Get the whole count
###        # ----------------------------------------------------------------------
###        count = data['Songs']['Year'].value_counts(sort=True, ascending=False)
###
###        # ----------------------------------------------------------------------
###        # Make the count into a dataframe and label the columns
###        # ----------------------------------------------------------------------
###        df = pd.DataFrame(list(zip(count.index.tolist(), count.tolist())), columns=["Year of Song's Origination","Number of Songs Played"])
###
###        # ----------------------------------------------------------------------
###        # Make it into a bar chart
###        # ----------------------------------------------------------------------
###        bar = px.bar(df, x="Year of Song's Origination", y="Number of Songs Played", barmode='group')
###
###        # ----------------------------------------------------------------------
###        # Update the design based on the config
###        # ----------------------------------------------------------------------
###        if 'style' in config: 
###            if 'backgroundColor' in config['style']:
###                bar.update_layout(plot_bgcolor=config['style']['backgroundColor'])
###                bar.update_layout(paper_bgcolor=config['style']['backgroundColor'])
###            if 'color' in config['style']:
###                bar.update_layout(font_color=config['style']['color'])
###
###        # ----------------------------------------------------------------------
###        # Send back the chart
###        # ----------------------------------------------------------------------
###        return bar
###
###    # --------------------------------------------------------------------------
###    # Finish (no call should reach this far, but just to be complete
###    # --------------------------------------------------------------------------
###    return False
