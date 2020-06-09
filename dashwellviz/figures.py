import textwrap

from plotly.subplots import make_subplots
import plotly.graph_objs as go
import seaborn as sns

from dashwellviz.utils import to_plotly_rgb


class WellLog:
    """Well log wrapper.

    Args:
        n_tracks (int): number of vertical tracks.
        shared_yaxes (bool): shared Y axes for all tracks?

    Other keyword arguments will be passed to plotly.make_subplots()

    Attributes:
        fig (plotly go.Figure object)

    """

    def __init__(self, n_tracks, shared_yaxes=True, **kwargs):
        self.fig = make_subplots(
            rows=1,
            cols=n_tracks,
            subplot_titles=[f"{t + 1}:" for t in range(n_tracks)],
            shared_yaxes=shared_yaxes,
            **kwargs,
        )

    def get_trace(self, name):
        """Get a dictionary containing the plotly graph object for the trace.

        Args:
            name (str): current name of the plotly graph object.

        Returns: dict containing key *'go'* containing the current plotly graph
            object, and other keys: *'track_no'* (int): zero-indexed track/column
            containing the trace.

        """
        trace = None
        for tr in self.fig.data:
            if tr.name == name:
                trace = {"go": tr}
        if trace is None:
            raise KeyError(
                f"Could not find trace.name = '{name}' in {[t['name'] for t in self.fig.data]}"
            )
        else:
            if trace["go"].yaxis == "y":
                trace["track_no"] = 0
            else:
                trace["track_no"] = int(trace["go"].yaxis.replace("y", "")) - 1

            return trace

    def add_trace(self, graph_obj, name=None, track_no=0, **kwargs):
        """Add a trace to the plotly figure.

        Args:
            graph_obj (plotly graph object)
            name (str)
            track_no (int): zero-indexed track/column number

        Other keyword arguments (e.g. "secondary_x") are passed through
        to plotly.go.Figure.add_trace.

        """
        if name is None:
            name = graph_obj.name
        self.fig.add_trace(graph_obj, row=1, col=track_no + 1, **kwargs)


def make_scatter(series, **kwargs):
    return go.Scatter(x=series.values, y=series.index, **kwargs)


def make_composite_log(
    df, lines=(), log_tracks=(), lines_func=make_scatter, line_kwargs=None
):
    """Make a composite well log from a pandas.DataFrame.

    Args:
        df (pandas.DataFrame): the index should be the depth.
        lines (list of lists): list of column names to plot as lines on
            the composite log. Each item should be a list of column names;
            each list refers to each track. So for example, for a composite
            log showing gamma in the first track and neutron and density in
            the second track, you would use: ``lines=[["GAMM"], ["NEUT", "RHO"]]``.
        log_tracks (list): list of tracks to set as log scale (zero-indexed,
            i.e. ``log_tracks=[0]`` would apply to left-most track; also
            allows negative indices so that ``log_tracks=[-1]`` would apply
            to the right-most track).
        lines_func (function): function which takes a pandas.Series and
            returns a plotly graph object e.g. ``go.Scatter``
        line_kwargs (dict): dictionary which is passed also for each
            call to lines_func. Default is `{"mode": "lines", "line": {"width": 1}}`

    Returns: ``WellLog`` object with a plotly ``Figure`` as the ``fig``
        attribute.

    """
    if line_kwargs is None:
        line_kwargs = {"mode": "lines", "line": {"width": 1}}
    n_tracks = max([len(lines)])

    columns = []
    log = WellLog(n_tracks=n_tracks)
    for i, column_names in enumerate(lines):
        for column in column_names:
            log.add_trace(
                lines_func(df[column], name=column, **line_kwargs), track_no=i
            )
            columns.append(column)

    data_range = df[columns].dropna(how="any")
    log.fig.update_yaxes(range=(max(data_range.index), min(data_range.index)))

    for track_no in log_tracks:
        if track_no < 0:
            track_no = n_tracks + track_no
        if track_no == 0:
            log.fig.update_layout(xaxis_type="log")
        else:
            log.fig.update_layout(**{f"xaxis{track_no + 1:.0f}_type": "log"})

    log.fig.update_layout(template="plotly_white")

    return log


def draw_strat(df, fig=None, seaborn_palette="pastel", **kwargs):
    """Draw stratigraphic intervals on a plotly Figure.

    Args:
        df (pandas.DataFrame): should have columns "depth_from", "depth_to"
            and "label". It can optionally have a column "colour" containing
            plotly-compatible colour definitions e.g. `'rgb(125, 0, 255)'`.
            If the latter does not existed it will be created and filled
            out using *seaborn_palette*.
        fig (plotly.go.Figure, optional): if omittted, a new plotly Figure
            will be created. If provided, the interval traces will be added
            using `fig.add_trace(xxx, **kwargs)`, so you can provide the
            keyword arguments *row* and *col* here to control whereabouts
            on your pre-existing plotly Figure the stratigraphic log
            will be added.
        seaborn_palette (str): see above.

    As described above, additional keyword arguments will be passed to
    ``fig.add_trace``.

    Returns: plotly Figure.

    """
    if fig is None:
        fig = go.Figure()

    # Get list of labels in stratigraphic order.
    df = df.sort_values(["depth_from", "depth_to"])
    seen = set()
    unique_labels = []
    for _, row in df.iterrows():
        if not row.label in seen:
            unique_labels.append(row.label)
            seen.add(row.label)

    colours = sns.color_palette(seaborn_palette, len(unique_labels))

    # Group by label (i.e. groupby stratigraphic unit)
    for label in unique_labels:
        dff = df[df.label == label]
        x = []
        y = []

        intervals = []
        for index, row in dff.iterrows():
            x.extend([0, 0, 1, 1, 0])
            y.extend(
                [
                    row.depth_to,
                    row.depth_from,
                    row.depth_from,
                    row.depth_to,
                    row.depth_to,
                ]
            )
            intervals.append(f"{row.depth_from:.0f}-{row.depth_to:.0f}")

        interval_label = label + " (" + ", ".join(intervals) + ")"

        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                fill="toself",
                fillcolor=(
                    row.colour
                    if row.colour
                    else to_plotly_rgb(*colours[unique_labels.index(label)])
                ),
                hoveron="fills",  # select where hover is active
                text=interval_label,
                name=row.label,
                hoverinfo="text+x+y",
                mode="lines",
                line=dict(width=0.4, color="white"),
            ),
            **kwargs,
        )

    # Extend figure range to maximum extent of stratigraphic layers.
    fig.update_yaxes(range=(df.depth_to.max(), df.depth_from.min()))

    return fig


def assign_colours_to_classes(df, seaborn_palette="pastel"):
    """Assign colours to lithology classes.

    Args:
        df (pandas.DataFrame): dataframe containing at least two
            columns: "class" (containing lithology class values e.g.
            `'sand'`, `'clay'`) and "colour" (containing a plotly-compatible
            colour definition e.g. `'rgb(125, 0, 255)'`)
        seaborn_palette (str): the seaborn palette which is used to
            generate colours for the different values in the dataframe's
            "class" column.

    This function generates a new colour for each unique value in `df["class"]`
    and assigns it into the `colour` column and returns the dataframe.

    Returns: the original dataframe, modified (a copy is not made).

    """
    unique_classes = list(df.loc[df["colour"].isnull(), "class"].unique())
    class_colours = sns.color_palette(seaborn_palette, len(unique_classes))

    existing_idx = ~df["colour"].isnull()
    existing_values = df.loc[existing_idx, "colour"].values

    idx = df["colour"].isnull()
    df.loc[idx, "colour"] = df.loc[idx, "class"].apply(
        lambda lith_class: to_plotly_rgb(
            *class_colours[unique_classes.index(lith_class)]
        )
    )
    return df


def draw_lith(df, fig=None, label_width=35, **kwargs):
    """Draw lithological descriptions on a plotly Figure.

    Args:
        df (pandas.DataFrame): should have columns "depth_from", "depth_to",
            "class", and "label". The column "class" should contain strings
            to apply colours to the chart e.g. values like `'sand'`, `'clay'`
            etc. The "label" column can have a detailed textual description.
            It should also have a column "colour" containing
            plotly-compatible colour definitions e.g. `'rgb(125, 0, 255)'`.
            See ``assign_colours_to_classes()`` in this module for how to
            ensure the dataframe is filled out with appropriate colours.
        fig (plotly.go.Figure, optional): if omittted, a new plotly Figure
            will be created. If provided, the interval traces will be added
            using `fig.add_trace(xxx, **kwargs)`, so you can provide the
            keyword arguments *row* and *col* here to control whereabouts
            on your pre-existing plotly Figure the stratigraphic log
            will be added.
        label_width (int): number of characters to wrap the labels on for
            the pop-up caption.

    As described above, additional keyword arguments will be passed to
    ``fig.add_trace``.

    Returns: plotly Figure.

    """
    if fig is None:
        fig = go.Figure()

    for index, row in df.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[0, 0, 1, 1],
                y=[row.depth_to, row.depth_from, row.depth_from, row.depth_to],
                fill="toself",
                fillcolor=row.colour,
                line_color="white",
                line=dict(width=0.4),
                hoveron="fills",  # select where hover is active
                text="<br />".join(
                    textwrap.wrap(
                        f"{row.depth_from:.2f}-{row.depth_to:.2f}m: {row.label}",
                        label_width,
                    )
                ),
                name=row["class"],
                hoverinfo="text+x+y",
                showlegend=False,
                mode="lines",
            ),
            **kwargs,
        )
    fig.update_yaxes(range=(df.depth_to.max(), df.depth_from.min()))
    return fig
