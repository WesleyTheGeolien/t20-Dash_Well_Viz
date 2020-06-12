

def to_plotly_rgb(r, g, b):
    """Convert seaborn-style colour tuple to plotly RGB string.

    Args:
        r (float): between 0 to 1
        g (float): between 0 to 1
        b (float): between 0 to 1

    Returns: a string for plotly

    """
    return f"rgb({r * 255:.0f}, {g * 255:.0f}, {b * 255:.0f})"