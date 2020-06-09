import dash
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


app = dash.Dash(__name__)

# load well data and plots from Doug 
# /Notebooks/dashwellviz WellLog example.ipynb
from welly import Well
import pandas as pd
w = Well.from_las('Data/Poseidon1Decim.LAS')
df = w.df()

# Generate Vp and Vs from DTco and DTsm
df['Vp'] = (1000000 / df['DTCO']) / 3.281
df['Vs'] = (1000000 / df['DTSM']) / 3.281
df['Vp_max'] = df['Vp'].max() + 200

# make cross plot 
fig = go.Figure(data=go.Scatter(
    x = df['Vp'],
    y = df['Vs'],
    mode='markers',
    opacity=0.7,
    marker=dict(
        size=8,
        color=df['NPHI'], #set color equal to a variable
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

# make log tracks
log_plot = make_subplots(rows=1, cols=3, subplot_titles=("Vp","Vs", "Rho"), shared_yaxes=True)

log_plot.add_trace(
    go.Scatter(x=df['Vp'], y=df.index),
    row=1, col=1,
)

log_plot.add_trace(
    go.Scatter(x=df['Vs'], y=df.index),
    row=1, col=2
)

log_plot.add_trace(
    go.Scatter(x=df['HROM'], y=df.index), 
    row=1, col=3
)

log_plot.update_yaxes(range=[5000, 4400])
log_plot.update_layout(template='plotly_white', height=1000, width=600, title_text="Vp Vs Rho Subplots")

# Create app layout
app.layout = html.Div([
    html.Div(
        className="app-header",
        children=[
            html.Div(className='header', children=[
                html.Div(className='logo_txt', children=[
                    html.Img(src='./assets/img/swung_round_no_text.png', height='75px', className='logo_img'),
                    html.Div('Dash Viz', className="app-header--title")
                ]),
                html.Div(className='project-subtitle', children=['A Transform 2020 Project'])
            ])
        ]
    ),


    html.Div(className='page', children=[
        html.Div(className='sidebar', children=[
            html.H1('Sidebar'),
            'Configuration tools (dropdowns etc.) can go in here)',
            dcc.Dropdown(placeholder="Select a well")
        ]),
        html.Div([
            html.H1('Well Plots Can Go Here'),
            html.Div(className='well-plot-container', children=[
                dcc.Graph(figure=log_plot) 
            ]),
        ]),
        
        html.Div(className='other-plot-container', children=[
            html.H1('Other Plots Can Go Here'),
            'cross plots, maps, etc',
            dcc.Graph(figure=fig)

        ]),



    ])
    
])

if __name__ == '__main__':
    app.run_server(debug=True)