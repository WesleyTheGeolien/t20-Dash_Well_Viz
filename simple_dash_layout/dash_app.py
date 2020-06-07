import dash
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(
        className="app-header",
        children=[
            html.Div(className='header', children=[
                html.Div(className='logo_txt', children=[
                    html.Img(src='./assets/img/swung_round_no_text.png', height='75px', className='logo_img'),
                    html.Div('Lash Template', className="app-header--title")
                ]),
                html.Div(className='project-subtitle', children=['A Transform 2020 Project'])
            ])
        ]
    ),


    html.Div(className='page', children=[
        html.Div(className='sidebar', children=[
            html.H1('Sidebar'),
            'Configuration tools (dropdowns etc.) can go in here)'
        ]),
        
        html.Div(className='well-plot-container', children=[
            html.H1('Well Plots Can Go Here') 
        ]),

        html.Div(className='other-plot-container', children=[
            html.H1('Other Plots Can Go Here'),
            'cross plots, maps, etc'

        ]),



    ])
    
])

if __name__ == '__main__':
    app.run_server(debug=True)