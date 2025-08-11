"""A reusable lead table."""
from dominate.tags import (div, span)  # noqa: F401


def value_badge(
        value,
        lower_threshold,
        upper_threshold,
        low='value-badge-low',
        mid='value-badge-mid',
        high='value-badge-high',
        text=None):
    """Create a badge based on value and thresholds."""
    # If value less than the lower_threshold, assign red.
    # If value greater than or equal to the upper_threshold, assign blue.
    # Else its in the middle so assign orange.
    display = text if text is not None else value
    if type(value) not in (int, float):
        return span(display)
    else:
        if float(value) < lower_threshold:
            value_badge_cls = low
        elif float(value) >= upper_threshold:
            value_badge_cls = high
        else:
            value_badge_cls = mid
    _span = span(display, cls=value_badge_cls)
    return _span


def stacked_freq_bar(counts, colours=['#9c9c9c', '#f39600', '#A53F97']):
    """Render a horizontal stacked bar showing each count's proportion of the total."""
    # Takes lists of counts and corresponding colours
    stacked_freq_bar = div(_class="stacked_freq_bar")
    for val, colour in zip(counts, colours):
        width_pct = f"{(int(val) / sum([int(x) for x in counts])) * 100:.2f}%"
        stacked_freq_bar.add(
            div(
                _class="bar",
                style=f"width: {width_pct}; background-color: {colour};"))
    return div(stacked_freq_bar, style="display: flex; justify-content: center;")
