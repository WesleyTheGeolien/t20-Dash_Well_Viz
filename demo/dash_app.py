# Import dash stuff
import dash
import dash_core_components as dcc
import dash_html_components as html

# Import graph objects (easier interface than the raw dictionnaries)
import plotly.graph_objs as go

# Create the dash app
app = dash.Dash(__name__)

# ------------------------------------------------------------------
# Create the Figures (copy paste from notebook)
x = [1,2,3]
y = [3,4,9]

trace = go.Scatter(
    x = x,
    y = y,
)

trace1 = go.Scatter(
    x = x,
    # Add 1 to the y values
    y = [val + 1 for val in y],
    mode='markers',
    name='test trace 2'
)

# figure expects data (traces) to be in an array
fig = go.Figure([trace, trace1])

# ------------------------------------------------------------------

app.layout = html.Div(children=[
    # Some text
    html.H1(children='My first Dash app'),

    # Some more text
    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    # Create the Graph
    dcc.Graph(
        id='example-graph',
        # Declare above
        figure=fig
    )
])

# if we are running this file (python dash_app.py) then launch
# the server
if __name__ == '__main__':
    app.run_server(debug=True, host='localhost')