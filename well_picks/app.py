import dash
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px

import numpy as np

app = Dash(__name__)
# Create server variable with Flask server object for use with gunicorn
server = app.server

sample_depth = np.arange(0, 10 * np.pi, 0.1)
sample_log1 = np.sin(sample_depth)

surface_picks = {"top_fm": 2, "base_fm": 4}
dropdown_options = [{'label': k, 'value': k} for k in list(surface_picks.keys())]

fig_well_1 = px.line(x=sample_log1, y=sample_depth)
fig_well_1.update_yaxes(autorange="reversed")

fig_well_1.update_layout(
    shapes=[
        dict(
            type="line",
            yref="y",
            y0=surface_picks["top_fm"],
            y1=surface_picks["top_fm"],
            xref="x",
            x0=-1,
            x1=1,
        )
    ]
)



app.layout = html.Div(
    children=[
        dcc.Dropdown(id='top-selector', options=dropdown_options, placeholder="Select a top to edit"),
        dcc.Graph(id="well_plot", figure=fig_well_1, style={'width': '40%', 'height':'1000px'}),
        
        #hidden_div for storing tops data
        html.Div(id='tops-storage', style={'display': 'none'})
    ]
)


@app.callback(Output("well_plot", "figure"),
 [Input("well_plot", "clickData"),
 Input("top-selector", "value")])
def display_click_data(clickData, top_to_edit):

    y = clickData['points'][0]['y']
    fig_well_1 = px.line(x=sample_log1, y=sample_depth)
    fig_well_1.update_yaxes(autorange="reversed")

    fig_well_1.update_layout(
        shapes=[dict(type="line", yref="y", y0=y, y1=y, xref="x", x0=-1, x1=1)]
    )
    return fig_well_1


app.run_server(port=8005, debug=True)