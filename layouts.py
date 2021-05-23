# ==================================================================================================
# All-Request-Thursdays data
# ==================================================================================================

# --------------------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------------------
import sys
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import plotly.express as px

from lib import *

from app import app

# --------------------------------------------------------------------------------------------------
# Store style components
# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Default
# ------------------------------------------------------------------------------
style_default = {}
style_default['backgroundColor']  = '#111111'
style_default['color']            = '#FFFFFF'
style_default['textAlign']        = 'center'

# --------------------------------------------------------------------------------------------------
# Sort out the data components
# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Get the data
# ------------------------------------------------------------------------------
data_fname = "data\\cholt_data.xlsx"
data = get_marked_data(data_fname)

# ------------------------------------------------------------------------------
# Get some universal metrics
# ------------------------------------------------------------------------------
total_shows        = len(data['Gigs'])
total_performances = len(data['Performances'])
total_songs        = len(data['Songs'])
total_albums       = len(data['Albums'])
total_artists      = len(data['Bands'])
min_year           = data['Songs']['Year'].min()
max_year           = data['Songs']['Year'].max()
year_span          = max_year - min_year + 1

# ------------------------------------------------------------------------------
# Get lists of particular things for filters
# ------------------------------------------------------------------------------
list_of_shownums      = sorted(data['Gigs']['Series Index'].to_list())
list_of_song_names    = sorted(data['Songs']['Name'].unique().tolist())
list_of_artists       = sorted(data['Bands']['Name'].tolist())


list_of_songs_artists = data['Songs'].index.to_list()
list_of_songs_artists = [x[1] + ": " + x[0] for x in list_of_songs_artists]

# ------------------------------------------------------------------------------
# Info about the navigable pages
# ------------------------------------------------------------------------------
pages = {}
pages['splash']        = {'href':"/"                 , 'name':"Home"         }
pages['performances']  = {'href':"/performances"     , 'name':"Performances" }
pages['shows']         = {'href':"/shows"            , 'name':"Shows"        }
pages['songs']         = {'href':"/songs"            , 'name':"Songs"        }
pages['albums']        = {'href':"/albums"           , 'name':"Albums"       }
pages['artists']       = {'href':"/artists"          , 'name':"Artists"      }
pages['people']        = {'href':"/people"           , 'name':"People"       }
pages['originals']     = {'href':"/originals"        , 'name':"Originals"    }

# ------------------------------------------------------------------------------
# Get the major data frames that we will need
# ------------------------------------------------------------------------------
data_performances = get_data_performances(data)
data_shows        = get_data_shows(data)
data_songs        = get_data_songs(data)
data_albums       = get_data_albums(data)
data_artists      = get_data_artists(data)
data_people       = get_data_people(data)
data_originals    = get_data_originals(data)

# ------------------------------------------------------------------------------
# Put together the blocks of text and image assets used in all sheets
# ------------------------------------------------------------------------------
title = "Chris Holt's All Request Thursdays, Live from CH Studio in Dallas TX"

logo = 'CH Plays.jpg'

footnote = {}
footnote['credits'] = "Data curated by Craig Adams with Graf Weller and Chris Holt.  Dashboard implementation by Grant Dickerson. Copyright 2021."
footnote['revnum']  = "Rev.6"

# --------------------------------------------------------------------------------------------------
# Layout - Splash page
# --------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Data, Charts, and Other Assets needed for this page
# ------------------------------------------------------------------------------
data_last_setlist = data_performances.loc[data_performances['Show']==max(data_performances['Show'])]

splash_image = 'ch1.png'

blurb_1 = "Chris Holt is an award-winning multi-instrumentalist and musical encyclopedia.  Prior to 2020, he made most of his living by playing live, mostly to local crowds in Dallas, but occasionally touring with Don Henley's band and sharing the stage with many of his musical heroes.  When the Covid-19 lockdowns changed the nature of what live performance had to be, Chris put his phone on a tripod and started streaming on Facebook once a week, working strictly on tips.  It's still going on.  Three hours a week, from 7pm to 10pm Central time on Thursdays, Chris works away at an endless list of requests from a group of his fans from all over the world.  He performs every piece himself, using his collection of instruments, by building up the layers of each song in loops, then finally performing each song in its entirety.  Each week he amazes his viewers by producing from scratch a full set of music from his vast store of knowledge, performed by a world-class musician."
blurb_2 = "So far, there have been {} shows in this series, in which Chris has done {} performances of {} songs from {} albums by {} artists, spanning {} years of music."
blurb_2 = blurb_2.format(str(total_shows), str(total_performances), str(total_songs), str(total_albums), str(total_artists), str(year_span))
blurb_3 = "All by himself, right in front of your eyes, song by song...welcome to the world of All Request Thursdays."
blurbs = [blurb_1, blurb_2, blurb_3]

data_num_songs_by_artist = get_data_num_songs_by_artist(data, minsongs=5)
data_num_songs_by_year   = get_data_num_songs_by_year(data)

chart_num_songs_by_artist = generate_bar(data_num_songs_by_artist, idx="chart_num_songs_by_artist", x="Originating Artist",          y="Number of Songs Played", color="CH Original", style=style_default)
chart_num_songs_by_year   = generate_bar(data_num_songs_by_year,   idx="chart_num_songs_by_year",   x="Year of Song's Origination",  y="Number of Songs Played"                     , style=style_default)

# ------------------------------------------------------------------------------
# Compile components
# ------------------------------------------------------------------------------
components = []
components.append(get_header(app, title, logo))
components.append(get_navbar(pages, 'splash'))
components.append(make_splash_page(app, splash_image, blurbs))
components.extend(display_simple_table(data_last_setlist, idx="splash_setlist_table", title="Setlist from latest show"))
components.extend(display_chart(shape="1x1", charts=[chart_num_songs_by_artist], title="Number of Songs by Artist (played at least five songs)"))
components.extend(display_chart(shape="1x1", charts=[chart_num_songs_by_year],   title="Number of Songs by Year of Origination"))
components.append(get_footnote(footnote))

# ------------------------------------------------------------------------------
# Top Level
# ------------------------------------------------------------------------------
layout_splash = html.Div(components, style=style_default)

# --------------------------------------------------------------------------------------------------
# Layout - Performances page
# --------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Data, Charts, and Other Assets needed for this page
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Compile components
# ------------------------------------------------------------------------------
components = []
components.append(get_header(app, title, logo))
components.append(get_navbar(pages, 'performances'))
components.extend(display_data_table(data_performances, idx="performances_data_table", title="Data by Performances", height="600px"))
components.append(get_footnote(footnote))

# ------------------------------------------------------------------------------
# Top Level
# ------------------------------------------------------------------------------
layout_performances = html.Div(components, style=style_default)

# --------------------------------------------------------------------------------------------------
# Layout - Shows page
# --------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Data, Charts, and Other Assets needed for this page
# ------------------------------------------------------------------------------
data_songs_by_show = data_shows.sort_values(by='Series Index')
chart_songs_by_show = generate_bar(data_songs_by_show, idx="chart_songs_by_show", x="Show Title", y="Count", style=style_default)

# ------------------------------------------------------------------------------
# Compile components
# ------------------------------------------------------------------------------
components = []
components.append(get_header(app, title, logo))
components.append(get_navbar(pages, 'shows'))
components.extend(display_data_table(data_shows, idx="shows_data_table", title="Data by Shows", height="250px"))
components.extend(display_chart(shape="1x1", charts=[chart_songs_by_show], title="Number of Songs Per Show"))
components.append(get_footnote(footnote))

# ------------------------------------------------------------------------------
# Top Level
# ------------------------------------------------------------------------------
layout_shows = html.Div(components, style=style_default)

# --------------------------------------------------------------------------------------------------
# Layout - Songs page
# --------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Data, Charts, and Other Assets needed for this page
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Compile components
# ------------------------------------------------------------------------------
components = []
components.append(get_header(app, title, logo))
components.append(get_navbar(pages, 'songs'))
components.extend(display_data_table(data_songs, idx="songs_data_table", title="Data by Songs", height="250px"))
components.append(get_footnote(footnote))

# ------------------------------------------------------------------------------
# Top Level
# ------------------------------------------------------------------------------
layout_songs = html.Div(components, style=style_default)

# --------------------------------------------------------------------------------------------------
# Layout - Albums page
# --------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Data, Charts, and Other Assets needed for this page
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Compile components
# ------------------------------------------------------------------------------
components = []
components.append(get_header(app, title, logo))
components.append(get_navbar(pages, 'albums'))
components.extend(display_data_table(data_albums, idx="albums_data_table", title="Data by Albums", height="300px"))
components.append(get_footnote(footnote))

# ------------------------------------------------------------------------------
# Top Level
# ------------------------------------------------------------------------------
layout_albums = html.Div(components, style=style_default)

# --------------------------------------------------------------------------------------------------
# Layout - Artists page
# --------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Data, Charts, and Other Assets needed for this page
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Compile components
# ------------------------------------------------------------------------------
components = []
components.append(get_header(app, title, logo))
components.append(get_navbar(pages, 'artists'))
components.extend(display_data_table(data_artists, idx="artists_data_table", title="Data by Artists", height="300px"))
components.append(get_footnote(footnote))

# ------------------------------------------------------------------------------
# Top Level
# ------------------------------------------------------------------------------
layout_artists = html.Div(components, style=style_default)

# --------------------------------------------------------------------------------------------------
# Layout - People page
# --------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Data, Charts, and Other Assets needed for this page
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Compile components
# ------------------------------------------------------------------------------
components = []
components.append(get_header(app, title, logo))
components.append(get_navbar(pages, 'people'))
components.extend(display_data_table(data_people, idx="people_data_table", title="Data by People", height="300px"))
components.append(get_footnote(footnote))

# ------------------------------------------------------------------------------
# Top Level
# ------------------------------------------------------------------------------
layout_people = html.Div(components, style=style_default)

# --------------------------------------------------------------------------------------------------
# Layout - Originals page
# --------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Data, Charts, and Other Assets needed for this page
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Compile components
# ------------------------------------------------------------------------------
components = []
components.append(get_header(app, title, logo))
components.append(get_navbar(pages, 'original'))
components.extend(display_data_table(data_originals, idx="originals_data_table", title="Data by Originals", height="300px"))
components.append(get_footnote(footnote))

# ------------------------------------------------------------------------------
# Top Level
# ------------------------------------------------------------------------------
layout_originals = html.Div(components, style=style_default)



