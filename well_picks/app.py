from welly import Well

import plotly.express as px
from dash import Dash, callback_context
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import json
import numpy as np
import pandas as pd
from pathlib import Path

import helper

app = Dash(__name__)
# Create server variable with Flask server object for use with gunicorn
server = app.server

# load well data
w = Well.from_las(str(Path("Data") / "Poseidon1Decim.LAS"))
df = w.df()

# sample pick data, eventually load from file or other source into dict
surface_picks = {"Montara Formation": 4620, "Plover Formation (Top Reservoir)": 4798.4}
dropdown_options = [{'label': k, 'value': k} for k in list(surface_picks.keys())]

# draw the initial plot
fig_well_1 = px.line(x=df['ECGR'], y=df.index)
fig_well_1.update_yaxes(autorange="reversed")
helper.update_picks_on_plot(fig_well_1, surface_picks)


app.layout = html.Div(
    children=[
        html.Div([
            'Edit tops:', 
            dcc.Dropdown(id='top-selector', options=dropdown_options, placeholder="Select a top to edit", style={'width': '200px'}),
            
            html.Hr(),
            'Create a new surface pick:', html.Br(),
            dcc.Input(id='new-top-name', placeholder='Name for new top', type='text', value=''),
            html.Button('Create', id='new-top-button'),
            
            html.Hr(),
            "Write tops to file:",
            dcc.Input(id='input-save-path', type='text', placeholder='path_to_save_picks.json', value=''),
            html.Button('Save Tops', id='save-button', n_clicks=0),
        ]),
        dcc.Graph(id="well_plot",
                    figure=fig_well_1,
                    style={'width': '40%', 'height':'900px'},
                    animate=True), # prevents axis rescaling on graph update
                    
        
        # hidden_div for storing tops data as json
        # Currently not hidden for debugging purposes. change style={'display': 'none'}
        html.Div(id='tops-storage', children=json.dumps(surface_picks)),#, style={'display': 'none'}),
        
        # hidden_div for storing un-needed output
        html.Div(id='placeholder', style={'display': 'none'})
    ],
    style={'display': 'flex'}
)

# update tops data when graph is clicked or new top is added
@app.callback(
    Output('tops-storage', 'children'),
    [Input('well_plot', 'clickData'),
     Input('new-top-button', 'n_clicks')],
    [State("top-selector", "value"),
     State("tops-storage", "children"),
     State('new-top-name', 'value')])
def update_pick_storage(clickData, new_top_n_clicks, active_pick, surface_picks, new_top_name):
    """Update the json stored in tops-storage div based on y-value of click"""
    
    # Each element in the app can only be updated by one call back function.
    # So anytime we want to change the tops-storage it has to be inside of this function.
    # We need to use the dash.callback_context to determine which event triggered
    # the callback and determine which actions to take
    # https://dash.plotly.com/advanced-callbacks    
    surface_picks = json.loads(surface_picks)
    
    # get callback context
    ctx = callback_context
    if not ctx.triggered:
        event_elem_id = 'No clicks yet'
    else:
        event_elem_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # do the updating based on context
    if event_elem_id == "well_plot": # click was on the plot
        if active_pick:
            y = clickData['points'][0]['y']

            # update the tops depth dict
            surface_picks[active_pick] = y
            surface_picks.pop("", None)

    if event_elem_id == "new-top-button": # click was on the new top button
        surface_picks[new_top_name] = "" # insert a new top

    return json.dumps(surface_picks)

# Update graph when tops storage changes
@app.callback(
    Output("well_plot", "figure"),
    [Input('tops-storage', 'children')])
def update_figure(surface_picks):
    """redraw the plot when the data in tops-storage is updated"""
    
    surface_picks = json.loads(surface_picks)
    # regenerate figure with the new horizontal line
    fig = px.line(x=df['ECGR'], y=df.index)
    fig.update_yaxes(autorange="reversed")
    helper.update_picks_on_plot(fig, surface_picks)
    
    return fig


@app.callback(
    Output("top-selector", "options"),
    [Input('tops-storage', 'children')])
def update_dropdown_options(surface_picks):
    """update the options available in the dropdown when a new top is added"""
    
    surface_picks = json.loads(surface_picks)

    dropdown_options = [{'label': k, 'value': k} for k in list(surface_picks.keys())]
    return dropdown_options

# Write tops to external file
@app.callback(
    Output('placeholder', 'children'),
    [Input('save-button', 'n_clicks')],
    [State('tops-storage', 'children'),
    State('input-save-path', 'value')])
def save_picks(n_clicks, surface_picks, path):
    """Save out picks to a csv file. 
    TODO: I am sure there are better ways to handle saving out picks, but this is proof of concept"""
    #picks_df = pd.read_json(surface_picks)

    if path:
        path_to_save = Path('.') / 'well_picks' / 'pick_data' / path
        with open(path_to_save, 'w') as f:
            json.dump(surface_picks, fp=f)

    return



if __name__ == "__main__":
    app.run_server(port=4545, debug=True)