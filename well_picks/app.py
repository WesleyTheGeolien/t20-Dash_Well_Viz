import plotly.express as px
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import json
import numpy as np

app = Dash(__name__)
# Create server variable with Flask server object for use with gunicorn
server = app.server

# Create sample well log data
sample_depth = np.arange(0, 10 * np.pi, 0.1)
sample_log1 = np.sin(sample_depth)

# sample pick data
surface_picks = {"pick_1": 2, "pick_2": 10, "pick_3": 14}
dropdown_options = [{'label': k, 'value': k} for k in list(surface_picks.keys())]

# draw the initial plot
fig_well_1 = px.line(x=sample_log1, y=sample_depth)
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
                xref="x",
                x0=-1,
                x1=1,
            ) 
            for top_name in surface_picks.keys()
        ]
    )

update_picks_on_plot(fig_well_1, surface_picks)


app.layout = html.Div(
    children=[
        dcc.Dropdown(id='top-selector', options=dropdown_options, placeholder="Select a top to edit", style={'width': '200px'}),
        dcc.Graph(id="well_plot", figure=fig_well_1, style={'width': '40%', 'height':'900px'}),
        
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
    fig = px.line(x=sample_log1, y=sample_depth)
    fig.update_yaxes(autorange="reversed")
    update_picks_on_plot(fig, surface_picks)
    
    return fig_well_1

app.run_server(port=4545, debug=True)