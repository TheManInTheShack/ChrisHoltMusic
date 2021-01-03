# ==============================================================================
# chproc
# Take simple input from individual show notes and break out the data into
# tables, updating the sheets in the advanced file for further markup
# ==============================================================================

# ------------------------------------------------------------------------------
# Import
# ------------------------------------------------------------------------------
from datetime import datetime
import os
import sys
import argparse
import shutil
import json

from itertools import product

import openpyxl as xl
import numpy as np
import pandas as pd
from py2neo import Graph, Node, Relationship

sys.path.append("S:\\IPS\\Voltron\\LIONS\\src\\Tools")

from io_tools import kill_program
from data_tools import valid_value, matrixify
from excel_tools import write_excel_sheet, apply_formatting_to_cell
from graph_tools import connect_to_open_graph, restart_graph


# ------------------------------------------------------------------------------
# Init
# ------------------------------------------------------------------------------
input_fname = "input/example_input.xlsx"
input_sheet = "Sheet1"

data_fname = "cholt_data.xlsx"

pd.set_option("display.width", 1000)
pd.set_option("display.max_rows", 50)
pd.set_option("display.max_columns", 20)


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
def main():
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("Starting...")

    # --------------------------------------------------------------------------
    # Get raw input
    # --------------------------------------------------------------------------
    input_data = parse_input_data(input_fname, input_sheet)

    # --------------------------------------------------------------------------
    # Parse the markup file
    # --------------------------------------------------------------------------
    existing_data = get_marked_data(data_fname)

    # --------------------------------------------------------------------------
    # Update tables - first by adding new stuff from the input, and then
    # enhancing it with second-order items
    # --------------------------------------------------------------------------
    updated_data = update_data_from_input(input_data, existing_data)
    updated_data = update_secondary_fields(updated_data)

    # --------------------------------------------------------------------------
    # Save new version to data for further markup
    # --------------------------------------------------------------------------
    o = save_updated_data(updated_data, data_fname)

    # --------------------------------------------------------------------------
    # Write the final processed data to the graph
    # --------------------------------------------------------------------------
    final_data = get_marked_data(data_fname)
    o = write_data_to_graph(final_data)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    print("...finished.")


# ------------------------------------------------------------------------------
# Get the raw data
# ------------------------------------------------------------------------------
def parse_input_data(input_fname, input_sheet):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...reading raw data from " + input_fname + "...")

    # --------------------------------------------------------------------------
    # Get the starting data
    # --------------------------------------------------------------------------
    raw_data = pd.read_excel(input_fname, sheet_name=input_sheet).dropna(how='all')

    # --------------------------------------------------------------------------
    # Work through the list
    # --------------------------------------------------------------------------
    current_date = None
    current_show_index = None
    current_show_title = None
    organized_records = []
    for i, rec in raw_data.iterrows():
        # ----------------------------------------------------------------------
        # From the unnamed first column, gather the date and show as they appear 
        # ----------------------------------------------------------------------
        if valid_value(rec[0]):
            # ------------------------------------------------------------------
            # The date will show up in the first row of each show
            # ------------------------------------------------------------------
            if isinstance(rec[0], datetime):
                current_date = rec[0]

            # ------------------------------------------------------------------
            # The shows in this series are just titled 'Episode n', which 
            # allows us to get the title and then extract the series index
            # Since this format means that the first item in each show doesn't
            # have the thing set yet, whenever we encounter it we also insert
            # it in the previous record
            # ------------------------------------------------------------------
            elif isinstance(rec[0], str):
                current_show_title = rec[0]
                current_show_index = int(rec[0].strip().lower().replace("episode ", ""))

                organized_records[-1]['show_title'] = current_show_title
                organized_records[-1]['show_index'] = current_show_index

            # ------------------------------------------------------------------
            # Those should be the only things there
            # ------------------------------------------------------------------
            else:
                print("WARNING!  UNRECOGNIZED DATA IN COLUMN A: " + rec[0])

        # ----------------------------------------------------------------------
        # Put together the record
        # ----------------------------------------------------------------------
        this_record = {}
        this_record['show_title'] = current_show_title
        this_record['show_index'] = current_show_index
        this_record['date'] = current_date
        this_record['song'] = rec['Song Title']
        this_record['artist'] = rec['Artist']
        this_record['album'] = rec['Album']
        this_record['year'] = rec['Release Year']
        this_record['notes'] = rec['Notes']

        # ----------------------------------------------------------------------
        # Add this record
        # ----------------------------------------------------------------------
        organized_records.append(this_record)

    # --------------------------------------------------------------------------
    # Consolidate
    # --------------------------------------------------------------------------
    input_data = organized_records

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return input_data

# ------------------------------------------------------------------------------
# Get the existing marked-up data, no frills
# ------------------------------------------------------------------------------
def get_marked_data(data_fname):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...reading data from file " + data_fname + "...")

    # --------------------------------------------------------------------------
    # Get the whole mess at once
    # --------------------------------------------------------------------------
    existing_data = pd.read_excel(data_fname, sheet_name=None, usecols = lambda x: 'Unnamed' not in x,)

    # --------------------------------------------------------------------------
    # Set up the index for each
    # --------------------------------------------------------------------------
    existing_data['People']       = existing_data['People'].set_index('Name', drop=False)
    existing_data['Instruments']  = existing_data['Instruments'].set_index('Name', drop=False)
    existing_data['Genres']       = existing_data['Genres'].set_index('Name', drop=False)
    existing_data['Bands']        = existing_data['Bands'].set_index('Name', drop=False)
    existing_data['Albums']       = existing_data['Albums'].set_index(['Name','Band'], drop=False)
    existing_data['Songs']        = existing_data['Songs'].set_index(['Name','Band'], drop=False)
    existing_data['Places']       = existing_data['Places'].set_index('Name', drop=False)
    existing_data['Series']       = existing_data['Series'].set_index('Name', drop=False)
    existing_data['Gigs']         = existing_data['Gigs'].set_index(['Series','Series Index'], drop=False)
    existing_data['Performances'] = existing_data['Performances'].set_index(['Series','Series Index','Set','Set Position'], drop=False)
    existing_data['Image']        = existing_data['Image'].set_index('File Name', drop=False)
    existing_data['Audio']        = existing_data['Audio'].set_index('File Name', drop=False)
    existing_data['Video']        = existing_data['Video'].set_index('File Name', drop=False)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return existing_data

# ------------------------------------------------------------------------------
# Update the tables that can be inferred to have new data
# ------------------------------------------------------------------------------
def update_data_from_input(input_data, existing_data):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...updating data tables...")

    # --------------------------------------------------------------------------
    # Start a new structure with the existing one
    # --------------------------------------------------------------------------
    updated_data = existing_data.copy()

    # --------------------------------------------------------------------------
    # Work back through the input
    # --------------------------------------------------------------------------
    set_position = 0
    current_show = 0
    for rec in input_data:
        # ----------------------------------------------------------------------
        # Bands
        # Collaborations are separated by the "/"
        # Key is just the name
        # ----------------------------------------------------------------------
        bands = rec['artist'].split("/")

        for band in bands:
            if not band in updated_data['Bands'].index:
                newrow = [{'Name': band}]
                newdata = pd.DataFrame(newrow).set_index('Name', drop=False)
                updated_data['Bands'] = updated_data['Bands'].append(newdata)

        # ----------------------------------------------------------------------
        # Albums
        # Key is the name of the album and the name of the band
        # ----------------------------------------------------------------------
        album = (rec['album'],rec['artist'])

        if not album in updated_data['Albums'].index:
            newrow = [{'Name':rec['album'], 'Band':rec['artist'], 'Year':rec['year']}]
            newdata = pd.DataFrame(newrow).set_index(['Name','Band'], drop=False)
            updated_data['Albums'] = updated_data['Albums'].append(newdata)

        # ----------------------------------------------------------------------
        # Songs
        # Medleys can be separated by "/"
        # Key is name of the song and name of the artist
        # ----------------------------------------------------------------------
        songs = rec['song'].split("/")

        for song in songs:
            idx = (rec['song'],rec['artist'])

            if not idx in updated_data['Songs'].index:
                newrow = [{'Name':rec['song'], 'Band':rec['artist'], 'Album':rec['album'], 'Year':rec['year']}]
                newdata = pd.DataFrame(newrow).set_index(['Name','Band'], drop=False)
                updated_data['Songs'] = updated_data['Songs'].append(newdata)

        # ----------------------------------------------------------------------
        # Gigs
        # This series is always from the same location and the start time is
        # assumed to be 7pm, so the only variable is date
        # ----------------------------------------------------------------------
        gig_loc = "CH Studio"
        gig_time = rec['date'].replace(hour=19)
        gig_series = "Live From CH Studio"
        idx = (gig_series, rec['show_index'])
        
        if not updated_data['Gigs'].index.isin([idx]).any():
            newrow = [{'Location':gig_loc, 'Date/Time Start':gig_time, 'Series':gig_series, 'Series Index':rec['show_index'], 'Show Title':rec['show_title']}]
            newdata = pd.DataFrame(newrow).set_index(['Series','Series Index'], drop=False)
            updated_data['Gigs'] = updated_data['Gigs'].append(newdata)

        # ----------------------------------------------------------------------
        # Performances
        # Medleys can be separated by "/"
        # Always only one Set
        # ----------------------------------------------------------------------
        songs = rec['song'].split("/")
        current_set = "I"

        for i, song in enumerate(songs):
            # ------------------------------------------------------------------
            # When we hit a new show, reset the index
            # Then increment the position
            # ------------------------------------------------------------------
            if not rec['show_index'] == current_show:
                current_show = rec['show_index']
                set_position = 0

            set_position += 1

            # ------------------------------------------------------------------
            # Figure out if this is part of a segue
            # ------------------------------------------------------------------
            segue_in = ""
            segue_out = ""
            if i > 0:
                segue_in = "Yes"
            if len(songs) > 1 and i < len(songs)-1:
                segue_out = "Yes"

            # ------------------------------------------------------------------
            # Set the index
            # ------------------------------------------------------------------
            idx = (gig_series, rec['show_index'], current_set, set_position)

            # ------------------------------------------------------------------
            # Add the new data
            # ------------------------------------------------------------------
            if not updated_data['Performances'].index.isin([idx]).any():
                # --------------------------------------------------------------
                # Compose the row
                # --------------------------------------------------------------
                newrec = {}
                newrec['Series'] = gig_series
                newrec['Series Index'] = rec['show_index']
                newrec['Set'] = current_set
                newrec['Set Position'] = set_position
                newrec['Song'] = song
                newrec['Artist'] = rec['artist']
                newrec['Segue In'] = segue_in
                newrec['Segue Out'] = segue_out
                newrec['Notes'] = rec['notes']

                newrow = [newrec]

                # --------------------------------------------------------------
                # Append that to the existing
                # --------------------------------------------------------------
                newdata = pd.DataFrame(newrow).set_index(['Series','Series Index','Set','Set Position'], drop=False)
                updated_data['Performances'] = updated_data['Performances'].append(newdata)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return updated_data

# ------------------------------------------------------------------------------
# Secondary updates - some fields feed each other
# ------------------------------------------------------------------------------
def update_secondary_fields(updated_data):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...updating secondary fields...")

    # --------------------------------------------------------------------------
    # People table can imply instruments via Instruments
    # People table can imply bands via Bands
    # --------------------------------------------------------------------------
    updated_data = update_field_from_other_field(updated_data, input_table="People", input_field="Instruments", output_table="Instruments", output_field="Name", delim="/")
    updated_data = update_field_from_other_field(updated_data, input_table="People", input_field="Bands", output_table="Bands", output_field="Name", delim="/")

    # --------------------------------------------------------------------------
    # Bands table can imply genres via Genres
    # --------------------------------------------------------------------------
    updated_data = update_field_from_other_field(updated_data, input_table="Bands", input_field="Genres", output_table="Genres", output_field="Name", delim="/")

    # --------------------------------------------------------------------------
    # Songs table can imply genres via Genre
    # Songs table can imply People via Writer
    # Songs table can imply Bands via Covered
    # --------------------------------------------------------------------------
    updated_data = update_field_from_other_field(updated_data, input_table="Songs", input_field="Genre", output_table="Genres", output_field="Name", delim="/")
    updated_data = update_field_from_other_field(updated_data, input_table="Songs", input_field="Writer", output_table="People", output_field="Name", delim="/")
    updated_data = update_field_from_other_field(updated_data, input_table="Songs", input_field="Covered", output_table="Bands", output_field="Name", delim="/")

    # --------------------------------------------------------------------------
    # TODO
    # Personnel on the Songs table is more complicated, e.g.:
    # Barry Gibb (Vocal,Rhythm Guitar),Robin Gibb (Vocal),Maurice Gibb (Vocal)
    # ...it needs to feed into both the People and the Instruments, and then
    # imply further relationships between those
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Gigs table can imply Series via Series
    # --------------------------------------------------------------------------
    updated_data = update_field_from_other_field(updated_data, input_table="Gigs", input_field="Series", output_table="Series", output_field="Name")

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return updated_data

# ------------------------------------------------------------------------------
# Adding items to a table based on contents of some field
# ------------------------------------------------------------------------------
def update_field_from_other_field(data, input_table, input_field, output_table, output_field, delim=None):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...implying new items from " + input_table + "/" + input_field + " to " + output_table + "/" + output_field + "...")

    # --------------------------------------------------------------------------
    # Go through the list
    # --------------------------------------------------------------------------
    for item in data[input_table][input_field].to_list():
        # ----------------------------------------------------------------------
        # Skip out if there's nothing there
        # ----------------------------------------------------------------------
        if not(valid_value(item)):
            continue

        # ----------------------------------------------------------------------
        # Make into a list 
        # ----------------------------------------------------------------------
        if delim:
            all_entries = item.split(delim)
        else:
            all_entries = [item]

        # ----------------------------------------------------------------------
        # Work through the whole list
        # ----------------------------------------------------------------------
        for entry in all_entries:
            # ------------------------------------------------------------------
            # If it's not there in the destination
            # ------------------------------------------------------------------
            if not data[output_table].index.isin([entry]).any():
                # --------------------------------------------------------------
                # Make the new row as its own dataframe
                # --------------------------------------------------------------
                newrow = [{output_field: entry}]
                newdata = pd.DataFrame(newrow).set_index(output_field, drop=False)

                # --------------------------------------------------------------
                # Add this new row to the collection
                # --------------------------------------------------------------
                data[output_table] = data[output_table].append(newdata)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return data

# ------------------------------------------------------------------------------
# Save out the new version
# ------------------------------------------------------------------------------
def save_updated_data(updated_data, data_fname):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...writing data to file " + data_fname + "...")

    # --------------------------------------------------------------------------
    # Start the document
    # --------------------------------------------------------------------------
    wb = xl.Workbook()
    default_sheet = wb.active
    wb.remove(default_sheet)

    # --------------------------------------------------------------------------
    # Each table in the set, in the order we found them
    # --------------------------------------------------------------------------
    for table in updated_data:
        # ----------------------------------------------------------------------
        # Format the cells to remove NaNs and get rid of the fancy indexing,
        # ----------------------------------------------------------------------
        output_data = updated_data[table]
        output_clean = output_data.replace(np.nan, '', regex=True).reset_index(drop=True)

        # ----------------------------------------------------------------------
        # Header
        # ----------------------------------------------------------------------
        header = list(output_clean.columns)
        body = output_clean.values.tolist()

        matrix = matrixify([[header],body])

        # ----------------------------------------------------------------------
        # Add formatting, some different depending on the table
        # ---------------------------------------------------------------------
        fmt = {}
        fmt['reverse_rows'] = [1]
        fmt['zoom'] = 80

        if table == "People":
            fmt['column_widths'] = [40,12,12,60,60,60,30,30]
            fmt['shrink_cols'] = ['G','H']
        elif table == "Instruments":
            fmt['column_widths'] = [20,30,60]
        elif table == "Genres":
            fmt['column_widths'] = [20,40,60,60]
        elif table == "Bands":
            fmt['column_widths'] = [60,40,60,30,30]
            fmt['shrink_cols'] = ['D','E']
        elif table == "Songs":
            fmt['column_widths'] = [60,60,60,12,30,40,60,30,30]
            fmt['shrink_cols'] = ['H','I']
        elif table == "Albums":
            fmt['column_widths'] = [60,60,12,60,20,60,30,30]
            fmt['shrink_cols'] = ['D','G','H']
        elif table == "Places":
            fmt['column_widths'] = [30,40,20,10,12,12,60]
        elif table == "Series":
            fmt['column_widths'] = [50,12,60]
        elif table == "Gigs":
            fmt['column_widths'] = [20,15,30,20,20,60,60]
        elif table == "Performances":
            fmt['column_widths'] = [20,15,10,10,60,60,10,10,10,12,12,12,60]
        elif table == "Image":
            fmt['column_widths'] = [30,20,20,60,10,10,30,20,30,60]
        elif table == "Audio":
            fmt['column_widths'] = [30,20,20,60,10,10,20,60]
        elif table == "Video":
            fmt['column_widths'] = [30,20,20,60,10,10,20,60]

        # ----------------------------------------------------------------------
        # Write the sheet
        # ----------------------------------------------------------------------
        o = write_excel_sheet(wb, table, matrix, fmt)

    # --------------------------------------------------------------------------
    # Save the file
    # --------------------------------------------------------------------------
    wb.save(data_fname)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return True

# ------------------------------------------------------------------------------
# Write these tables to the graph as needed
# ------------------------------------------------------------------------------
def write_data_to_graph(final_data):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...writing data to graph...")

    # --------------------------------------------------------------------------
    # Connect to the graph
    # --------------------------------------------------------------------------
    graph = connect_to_open_graph(pwd="cholt123")

    # --------------------------------------------------------------------------
    # Restart the data if called to do so
    # --------------------------------------------------------------------------
    restart = True
    x = restart_graph(graph, do=restart)

    # --------------------------------------------------------------------------
    # Add all of the nodes and their static properties
    # --------------------------------------------------------------------------
    n = add_nodes_from_df(graph, label="Person"      , frame=final_data["People"]       , props=['Year Born','Year Died','Notes'])
    n = add_nodes_from_df(graph, label="Instrument"  , frame=final_data["Instruments"]  , props=['Type','Notes'])
    n = add_nodes_from_df(graph, label="Genre"       , frame=final_data["Genres"]       , props=['Features','Notes'])
    n = add_nodes_from_df(graph, label="Band"        , frame=final_data["Bands"]        , props=['Notes'])
    n = add_nodes_from_df(graph, label="Song"        , frame=final_data["Songs"]        , props=['Year','Writer','Notes'])
    n = add_nodes_from_df(graph, label="Album"       , frame=final_data["Albums"]       , props=['Year','Notes'])
    n = add_nodes_from_df(graph, label="Place"       , frame=final_data["Places"]       , props=['Address','City','State','Latitude','Longitude','Notes'])
    n = add_nodes_from_df(graph, label="Series"      , frame=final_data["Series"]       , props=['Active','Notes'])
    n = add_nodes_from_df(graph, label="Gig"         , frame=final_data["Gigs"]         , props=['Date/Time Start','Date/Time End','Show Title','Notes'])
    n = add_nodes_from_df(graph, label="Performance" , frame=final_data["Performances"] , props=['Segue In','Segue Out','Looping','Notes'])
    n = add_nodes_from_df(graph, label="Image"       , frame=final_data["Image"]        , props=['File Path','Title','Format','Size_X','Size_Y','Photographer','Timestamp','Notes'])
    n = add_nodes_from_df(graph, label="Audio"       , frame=final_data["Audio"]        , props=['File Path','Title','Format','Length','Notes'])
    n = add_nodes_from_df(graph, label="Video"       , frame=final_data["Video"]        , props=['File Path','Title','Format','Size_X','Size_Y','Length','Notes'])

    # --------------------------------------------------------------------------
    # Add the straightforward relationships 
    # add_relationships_from_df(graph, frame, origin_node, label, destination_node, destination_ref, delim=None, props={}):
    # --------------------------------------------------------------------------
    r = add_relationships_from_df(graph, final_data["People"]         , "Person"       , "PLAYS"        , "Instrument" , ['Instruments']           , delim="/" , props=[])
    r = add_relationships_from_df(graph, final_data["People"]         , "Person"       , "MEMBER_OF"    , "Band"       , ['Bands']                 , delim="/" , props=[])
    r = add_relationships_from_df(graph, final_data["Bands"]          , "Band"         , "PLAYS_GENRE"  , "Genre"      , ['Genres']                , delim="/" , props=[])
    r = add_relationships_from_df(graph, final_data["Songs"]          , "Song"         , "IS_GENRE"     , "Genre"      , ['Genre']                 , delim="/" , props=[])
    r = add_relationships_from_df(graph, final_data["Songs"]          , "Song"         , "BY_BAND"      , "Band"       , ['Band']                  , delim="/" , props=[])
    r = add_relationships_from_df(graph, final_data["Songs"]          , "Song"         , "COVERED_BY"   , "Band"       , ['Covered']               , delim="/" , props=[])
    r = add_relationships_from_df(graph, final_data["Songs"]          , "Song"         , "ON_ALBUM"     , "Album"      , ['Album','Band']                      , props=[])
    r = add_relationships_from_df(graph, final_data["Songs"]          , "Song"         , "WRITTEN_BY"   , "Person"     , ['Writer']                , delim="/" , props=[])
    r = add_relationships_from_df(graph, final_data["Albums"]         , "Album"        , "IS_GENRE"     , "Genre"      , ['Genre']                 , delim="/" , props=[])
    r = add_relationships_from_df(graph, final_data["Gigs"]           , "Gig"          , "IN_SERIES"    , "Series"     , ['Series']                , delim="/" , props=[])
    r = add_relationships_from_df(graph, final_data["Gigs"]           , "Gig"          , "AT_LOCATION"  , "Place"      , ['Location']              , delim="/" , props=[])
    r = add_relationships_from_df(graph, final_data["Performances"]   , "Performance"  , "AT_GIG"       , "Gig"        , ['Series','Series Index']             , props=[])
    r = add_relationships_from_df(graph, final_data["Performances"]   , "Performance"  , "OF_SONG"      , "Song"       , ['Song','Artist']                     , props=['Segue In','Segue Out','Partial'])

    # --------------------------------------------------------------------------
    # TODO
    # Personnel on the Songs table is more complicated, e.g.:
    # Barry Gibb (Vocal,Rhythm Guitar),Robin Gibb (Vocal),Maurice Gibb (Vocal)
    # ...it needs to feed into both the People and the Instruments, and then
    # imply further relationships between those
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # TODO 
    # Performances should have Previous/Next links to each other within sets
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return True

# ------------------------------------------------------------------------------
# Given a data frame, add nodes to the graph
# ------------------------------------------------------------------------------
def add_nodes_from_df(graph,label,frame,props):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...adding nodes of type " + label + "...")

    # --------------------------------------------------------------------------
    # Go through each line
    # --------------------------------------------------------------------------
    for rec in frame.index:
        # ----------------------------------------------------------------------
        # Get the data for this record
        # ----------------------------------------------------------------------
        data = frame.loc[rec]

        # ----------------------------------------------------------------------
        # Format the key by forcing everything to a tuple and then doing a
        # simple pipe join for the whole thing into a string
        # ----------------------------------------------------------------------
        if not isinstance(rec, tuple):
            rec = tuple([rec])

        key = "|".join([str(x) for x in rec])

        # ----------------------------------------------------------------------
        # Make the simple node
        # ----------------------------------------------------------------------
        n = Node(label, ref=key)

        # ----------------------------------------------------------------------
        # Everything in the key becomes a property
        # ----------------------------------------------------------------------
        for i, prop in enumerate(frame.index.names):
            n[prop] = str(key.split("|")[i])

        # ----------------------------------------------------------------------
        # Add the static properties
        # ----------------------------------------------------------------------
        for prop in props:
            if valid_value(data[prop]):
                n[prop] = str(data[prop])

        # ----------------------------------------------------------------------
        # Merge the node into the graph
        # ----------------------------------------------------------------------
        graph.merge(n, label, "ref")

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return True


# ------------------------------------------------------------------------------
# Given a data frame, add nodes to the graph
# r = add_relationships_from_df(graph, 
#                               frame=final_data["People"], 
#                               origin_node="Person", 
#                               label="PLAYS",     
#                               destination_node="Instrument", 
#                               destination_ref=['Instruments'], 
#                               delim="/", 
#                               props={})
# ------------------------------------------------------------------------------
def add_relationships_from_df(graph, frame, origin_node, label, destination_node, destination_ref, delim=None, props={}):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...adding relationships of type " + label + "...")

    # --------------------------------------------------------------------------
    # Set the relationship 'Type'
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Go through each line
    # --------------------------------------------------------------------------
    for rec in frame.index:
        # ----------------------------------------------------------------------
        # Get the data for this record
        # ----------------------------------------------------------------------
        data = frame.loc[rec].to_dict()

        # ----------------------------------------------------------------------
        # Format the key by forcing everything to a tuple and then doing a
        # simple pipe join for the whole thing into a string
        # ----------------------------------------------------------------------
        if not isinstance(rec, tuple):
            rec = tuple([rec])

        origin_key = "|".join([str(x) for x in rec])

        # ----------------------------------------------------------------------
        # Find the origin node (there will only be one with the proper key)
        # ----------------------------------------------------------------------
        from_node = graph.nodes.match(origin_node, ref=origin_key).first()

        # ----------------------------------------------------------------------
        # Get the destination key(s).  There may be multiple fields in the key
        # and there might be multiple references in each field, so we need
        # to make an exploded version
        # First compile everything that we might need
        # ----------------------------------------------------------------------
        dest_data = []
        for col in destination_ref:
            # ------------------------------------------------------------------
            # Get the data from this cell
            # ------------------------------------------------------------------
            sdata = data[col]

            # ------------------------------------------------------------------
            # Make it into a list
            # ------------------------------------------------------------------
            if delim:
                if valid_value(sdata):
                    ldata = str(sdata).split(delim)
                else:
                    ldata = []
            else:
                if valid_value(sdata):
                    ldata = [sdata]
                else:
                    ldata = []

            # ------------------------------------------------------------------
            # Add to the list of lists
            # ------------------------------------------------------------------
            dest_data.append(ldata)

        # ----------------------------------------------------------------------
        # Then make an exploded list out of those
        # ----------------------------------------------------------------------
        full_dest = list(product(*dest_data))

        # ----------------------------------------------------------------------
        # Make the relationship for each
        # ----------------------------------------------------------------------
        for ddata in full_dest:
            # ------------------------------------------------------------------
            # Find the destination key
            # ------------------------------------------------------------------
            dest_key = "|".join([str(x) for x in ddata])

            # ------------------------------------------------------------------
            # Use that to find the node matching that key
            # ------------------------------------------------------------------
            to_node = graph.nodes.match(destination_node, ref=dest_key).first()

            if not(to_node):
                kill_program("INCONSISTENT DATA: No node matched for " + destination_node + " : " + dest_key)

            # ------------------------------------------------------------------
            # Make the relationship
            # ------------------------------------------------------------------
            r = Relationship(from_node, label, to_node)

            # ------------------------------------------------------------------
            # Add any properties
            # ------------------------------------------------------------------
            if props:
                pass

            # ------------------------------------------------------------------
            # Merge the relationship on to the graph
            # ------------------------------------------------------------------
            graph.merge(r)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return True

# ------------------------------------------------------------------------------
# Run
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    start_time = datetime.utcnow()
    main()
    end_time     = datetime.utcnow()
    elapsed_time = end_time - start_time
    print("Elapsed time: " + str(elapsed_time))
