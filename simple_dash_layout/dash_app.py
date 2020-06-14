import dash
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

import dashwellviz.figures
try:
    import helper
except:
    import simple_dash_layout.helper as helper

# Load Data
data_df = helper.load_data()
data_df = helper.add_vp_vs(data_df)

# set up options for dropdown selectors
data_labels_dict = [{'label': c, 'value': c} for c in data_df.columns]

list_of_well_names = ['Poseidon 1', 'Placeholder well 2 (no data here)']
well_names_labels_dict = [{'label': w, 'value': w} for w in list_of_well_names] 


# Create log plot from prebuilt figures
# In order to work with the checkbox idea, plot constructor will need to accept a list of logs.
# I think that means for now, that means we are restricted to only one log per track, and no logoritmic tracks. 
# We will need to find a better way to select the logs and define track properties

log_trace_fig = helper.composite_plot_from_list_of_log_names(data_df, ['ECGR', 'Vp', 'Vs', 'HROM'])

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

server = app.server

# Create app layout
app.layout = html.Div([
    
    helper.get_header(),

    html.Div(className='page', children=[

        html.Div(className='sidebar', children=[
            html.H1('Sidebar'),
            dcc.Dropdown(id='well-selector', placeholder="Select a well", options=well_names_labels_dict, value='Poseidon 1'),
            dcc.Checklist(id='curve-selectors', 
                          options=data_labels_dict, 
                          style={'display': 'inline-block'}, 
                          value=['ECGR', 'Vp', 'Vs', 'HROM']), # TODO: properly layout checkbox elements
            
            html.H2('Crossplot Options'),

            html.H4('Cross Plot Y Axis'),
            dcc.Dropdown(id='x-plot-y-axis', placeholder='Select a log curve', options=data_labels_dict, value='Vs'),

            html.H4('Cross Plot X Axis'),
            dcc.Dropdown(id='x-plot-x-axis', placeholder='Select a log curve', options=data_labels_dict, value='Vp'),
            
            html.H4('Cross Plot Marker Color'),
            dcc.Dropdown(id='x-plot-color', placeholder='Select a log curve', options=data_labels_dict, value='ECGR'),
            
            # TODO implement cross plot marker size
            # html.H4('Cross Plot Marker Size'), 
            # dcc.Dropdown(id='x-plot-size', placeholder='Select a log curve', options=data_labels_dict),
            
            html.H2('Histogram Options'),
            html.H4('Histogram Column'),
            dcc.Dropdown(id='hist-column', placeholder='Select a log curve', options=data_labels_dict),
        ]),

        html.Div([
            html.H1('Poseidon 1', id='log-plot-header', style={'text-align': 'center'}),
            html.Div(className='well-plot-container', children=[
                dcc.Graph(id='log-trace-plot', figure=log_trace_fig) 
            ]),
        ]),
    
        html.Div(className='other-plot-container', children=[
            html.H1('Other Plots Can Go Here'),
            'cross plots, maps, etc',
            html.Div(children=[
                dcc.Graph(id='single-w-cross-plot', figure=fig),                
                dcc.Graph(id='single-w-cross-plot2', figure=fig),
            ]),

        ]),
    ])
])

# Cross plot axis options
# TODO add marker size option
@app.callback(
    Output('single-w-cross-plot', 'figure'),
    [Input('x-plot-y-axis', 'value'),
    Input('x-plot-x-axis', 'value'),
    Input('x-plot-color', 'value')])
def update_cross_plot(y_axis, x_axis, color):

    # Update cross plot 
    # TODO this really, really needs to be abstracted 
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

# well dropdown. Currently updates log plot title
@app.callback(
    Output('log-plot-header', 'children'),
    [Input('well-selector', 'value')])
def update_well_name_in_title(value):
    return value

# Choose the displayed log curves from checkbox
@app.callback(
    Output('log-trace-plot', 'figure'),
    [Input('curve-selectors', 'value')])
def update_log_plots_on_curve_selection(curve_names):
    return helper.composite_plot_from_list_of_log_names(data_df, curve_names)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')