import dash
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

import dashwellviz.figures
import helper

# Load Data
data_df = helper.load_data()
data_df = helper.add_vp_vs(data_df)
data_labels_dict = [{'label': c, 'value': c} for c in data_df] # format options for selector dropdowns

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
        color=data_df['ECGR'], #set color equal to a variable
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
            dcc.Dropdown(id='well-selector', placeholder="Select a well"),
            dcc.Checklist(id='curve-selectors', options=data_labels_dict, style={'display': 'inline-block'}), # TODO: layout checkbox elements
            
            html.H2('Crossplot Options'),

            html.H4('Cross Plot Y Axis'),
            dcc.Dropdown(id='x-plot-y-axis', placeholder='Select a log curve', options=data_labels_dict, value='Vs'),

            html.H4('Cross Plot X Axis'),
            dcc.Dropdown(id='x-plot-x-axis', placeholder='Select a log curve', options=data_labels_dict, value='Vp'),
            
            html.H4('Cross Plot Marker Color'),
            dcc.Dropdown(id='x-plot-color', placeholder='Select a log curve', options=data_labels_dict, value='ECGR'),
            
            html.H4('Cross Plot Marker Size'), 
            dcc.Dropdown(id='x-plot-size', placeholder='Select a log curve', options=data_labels_dict),
            
            html.H2('Histogram Options'),
            html.H4('Histogram Column'),
            dcc.Dropdown(id='hist-column', placeholder='Select a log curve', options=data_labels_dict),
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
            html.Div(
                dcc.Graph(id='single-w-cross-plot', figure=fig)
            ),

        ]),
    ])
])

# Cross plot options
@app.callback(
    Output('single-w-cross-plot', 'figure'),
    [Input('x-plot-y-axis', 'value'),
    Input('x-plot-x-axis', 'value'),
    Input('x-plot-color', 'value')])
def update_cross_plot(y_axis, x_axis, color):
    
    # TODO this really, really needs to be abstracted
    # make cross plot 
    fig = go.Figure(data=go.Scatter(
        x = data_df[x_axis],
        y = data_df[y_axis],
        mode='markers',
        opacity=0.7,
        marker=dict(
            size=8,
            color=data_df[color], #set color equal to a variable
            colorscale='turbid', # one of plotly colorscales
            line=dict(
                color='black',
                width=1
            ),
            showscale=True
        )
    ))
    fig.update_xaxes(title_text=x_axis)
    fig.update_yaxes(title_text=y_axis)
    fig.update_layout(template='plotly_white', height=800, width=800, title_text=f"Vp Vs Xplot - coloured by {color}")

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='localhost')