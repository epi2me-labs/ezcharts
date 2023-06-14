"""Sunburst plots."""

from ezcharts.plots import _NoAxisFixPlot, util


__all__ = ["sunburst"]


def sunburst(
    data, tooltip=True, visualMap=True, min_value=0, max_value=None,
    color_scale=None, label_rotate="radial", label_minAngle=0, show_label=True
):
    """Create sunburst plot.

    :param data (list): List of nested dictionaries of the following structure:
        E.g.: `[{'name': 'parent A', 'value': X+Y, 'children':[
        {'name': 'child A1', 'value': X}, {'name': 'child A2', 'value': Y}
        ] },
        ...
        ]`.
    :param tooltip (bool): Enable/Disable tooltip.
    :param visualMap (bool): Enable/Disable `visualMap`. By default `visualMap` colors
        each section by their `value`. Color gradient is controlled with `min_value` and
        `max_value`.
    :param min_value (int): Minimum value.
    :param max_value (int): Maximum value.
    :param color_scale (list): List of colors to establish a gradient between
        `min_value` and `max_value`.
    :param label_rotate (int, str): If it is number type, then is stands for rotation,
        from -90 degrees to 90 degrees, and positive values stand for counterclockwise.
        It can also be 'radial' (along the radius) or 'tangential' (perpendicular to
        the radius).
    :param label_minAngle (int): Do not display the text if angle of data piece is
        smaller than this value (in degrees).
    :param show_label (bool): Whether to show labels.
    :return (plot): Sunburst plot.
    """
    plt = _NoAxisFixPlot()  # we don't have an axis so no point trying to fix
    plt.xAxis = dict(show=False)
    plt.yAxis = dict(show=False)
    plt.add_series(
        dict(
            type="sunburst",
            data=data,
            radius=[0, "100%"],
            emphasis=dict(focus="ancestor"),
            label=dict(
                rotate=label_rotate, minAngle=label_minAngle, show=show_label),
        )
    )
    # Enable tooltip
    if tooltip:
        plt.tooltip = dict(trigger="item")
    # Enable visualMap to color portions according to their abundance
    if visualMap:
        if max_value is None:
            # There are two options, all the levels can have their own values or just
            # the terminal children nodes. In this case, parent level values are
            # calculated adding the terminal values.
            # Check this and calculate max_value depending on input data.
            # if the first element have its own value:
            if data[0].get('value'):
                max_value = max({i.get("value") for i in data})
            else:
                max_value = sum_terminal_nodes(data)
        if not color_scale:
            color_scale = util.choose_palette('crest')
        plt.visualMap = [
            dict(
                type="continuous",
                min=min_value,
                max=max_value,
                inRange=dict(color=color_scale),
            )
        ]

    return plt


def sum_terminal_nodes(node):
    """Get the sum of the terminal nodes.

    :param node (dictionary): dictionary that contains name, value (optional) and
        and children (optional).
    :return (int): sum of the terminal nodes.
    """
    if "children" in node:
        # recursive case
        total = 0
        for child in node["children"]:
            total += sum_terminal_nodes(child)
        return total
    else:
        # base case
        return node["value"]
