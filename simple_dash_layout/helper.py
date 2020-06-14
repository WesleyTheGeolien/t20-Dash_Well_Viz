# TODO this file should probably only be ephemere during developement and used to abstract the  dash app

import dash_html_components as html

import dashwellviz
from welly import Well
import pandas as pd

def load_data(filename='Data/Poseidon1Decim.LAS'):
    """Fake data loader

    Returns:
        pandas.DataFrame: Dataframe containing info
    """
    w = Well.from_las(filename)
    return w.df()

def add_vp_vs(df):
    """Calculates the Vp and Vs for a las file

    Args:
        df (Pandas.DataFrame): input dataframe MUST CONTAIN `DTCO` and `DTSM`
    Returns:
        pandas.DataFrame: input dataframe with vp and vs calculated
    """
    df['Vp'] = (1000000 / df['DTCO']) / 3.281
    df['Vs'] = (1000000 / df['DTSM']) / 3.281
    df['Vp_max'] = df['Vp'].max() + 200
    return df

def get_header():
    """Header abstraction

    Returns:
        [type]: [description]
    """
    return html.Div(
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
    )

def composite_plot_from_list_of_log_names(data_df, curve_names):

    """Abstraction for creating the log plot from the checkbox

    In order to work with the checkbox idea, the plot constructor will need to accept a list of logs.
    I think that means for now, that means we are restricted to only one log per track, and no logoritmic tracks. 
    We will need to find a better way to select the logs and define track properties
    
    Args:
        curve_names (list): List of curve names to plot
    Returns:
        plotly figure
    """
    log = dashwellviz.figures.make_composite_log(
        data_df, lines=[[curve] for curve in curve_names]
    )

    log_trace_fig = log.fig
    log_trace_fig.update_layout(template='plotly_white', height=800, width=800)
    return log_trace_fig