
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
        ], # list comprehension iterating over the surface picks dictionary

        annotations=[
            dict(
                x=.5,
                y=surface_picks[top_name],
                xref="paper",
                yref="y",
                text=top_name,
                ax=0,
                ay=-8
            )
            for top_name in surface_picks.keys()
        ]
    )