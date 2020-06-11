from welly import Well

import plotly.express as px
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import json
import numpy as np
from pathlib import Path

app = Dash(__name__)
# Create server variable with Flask server object for use with gunicorn
server = app.server

# load well data
w = Well.from_las(str(Path("Data") / "Poseidon1Decim.LAS"))
df = w.df()

# sample pick data
surface_picks = {"Montara Formation": 4620, "Plover Formation (Top Reservoir)": 4798.4}
dropdown_options = [{'label': k, 'value': k} for k in list(surface_picks.keys())]

# draw the initial plot
fig_well_1 = px.line(x=df['ECGR'], y=df.index)
fig_well_1.update_yaxes(autorange="reversed")

def update_picks_on_plot(fig, surface_picks):
    """Draw horizontal lines on a figure at the depths of the values in the
       surface picks dictionary"""

    fig.update_layout(
        shapes=[
            dict(
                type="line",
                yref="y",
                y0=surface_picks[top_name],
                y1=surface_picks[top_name],
                xref="paper",
                x0=0 ,  
                x1=1,   # https://github.com/plotly/plotly_express/issues/143#issuecomment-535494243
            ) 
            for top_name in surface_picks.keys()
        ] # list comprehension iterating over the surface picks dictionary
    )

update_picks_on_plot(fig_well_1, surface_picks)


app.layout = html.Div(
    children=[
        dcc.Dropdown(id='top-selector', options=dropdown_options, placeholder="Select a top to edit", style={'width': '200px'}),
        dcc.Graph(id="well_plot",
                    figure=fig_well_1,
                    style={'width': '40%', 'height':'900px'},
                    animate=True), # prevents axis rescaling on graph update
                    
        
        #hidden_div for storing tops data
        # Currently not hidden for debugging purposes. change style={'display': 'none'}
        html.Div(id='tops-storage', children=json.dumps(surface_picks), style={}),
    ],
    style={'display': 'flex'}
)

@app.callback(Output('tops-storage', 'children'),
    [Input('well_plot', 'clickData'),],
    [State("top-selector", "value"),])
def update_pick_storage(clickData, active_pick):
    """Update the json stored in tops-storage div based on y-value of click"""
    if active_pick:
        y = clickData['points'][0]['y']

        # update the tops depth dict
        surface_picks[active_pick] = y
        update_picks_on_plot(fig_well_1, surface_picks)

        surface_picks.pop("null", None)

        return json.dumps(surface_picks)
    

@app.callback(
    Output("well_plot", "figure"),
    [Input('tops-storage', 'children')])
def update_figure(surface_picks):
    """redraw the plot when the data in tops-storage is updated"""
    
    surface_picks = json.loads(surface_picks)
    # regenerate figure with the new horizontal line
    fig = px.line(x=df['ECGR'], y=df.index)
    fig.update_yaxes(autorange="reversed")
    update_picks_on_plot(fig, surface_picks)
    
    return fig_well_1

app.run_server(port=4545, debug=True)