import dash
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


# import plotly.express as px
import plotly.graph_objs as go
# from plotly.subplots import make_subplots

import dashwellviz.figures
import helper

# Load Data
data_df = helper.load_data()
data_df = helper.add_vp_vs(data_df)

# Create log plot from prebuilt figures
log = dashwellviz.figures.make_composite_log(
    data_df, lines=[["Vp"], ["Vs"], ["HROM"], ["ATRX", "ATRT"]], log_tracks=[3]
)

log_trace_fig = log.fig
log_trace_fig.update_layout(template='plotly_white', height=800, width=800)

# TODO this needs to be abstracted
# make cross plot 
fig = go.Figure(data=go.Scatter(
    x = data_df['Vp'],
    y = data_df['Vs'],
    mode='markers',
    opacity=0.7,
    marker=dict(
        size=8,
        color=data_df['NPHI'], #set color equal to a variable
        colorscale='turbid', # one of plotly colorscales
        line=dict(
            color='black',
            width=1
        ),
        showscale=True
    )
))
fig.update_xaxes(title_text='Vp')
fig.update_yaxes(title_text='Vs')
fig.update_layout(template='plotly_white', height=800, width=800, title_text="Vp Vs Xplot - coloured by GR")

# Create the app
app = dash.Dash(__name__)

# Create app layout
app.layout = html.Div([
    
    helper.get_header(),

    html.Div(className='page', children=[

        html.Div(className='sidebar', children=[
            html.H1('Sidebar'),
            'Configuration tools (dropdowns etc.) can go in here)',
            dcc.Dropdown(placeholder="Select a well")
        ]),

        html.Div([
            html.H1('Well Plots Can Go Here'),
            html.Div(className='well-plot-container', children=[
                dcc.Graph(figure=log_trace_fig) 
            ]),
        ]),
    
        html.Div(className='other-plot-container', children=[
            html.H1('Other Plots Can Go Here'),
            'cross plots, maps, etc',
            dcc.Graph(figure=fig)

        ]),
    ])
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='localhost')