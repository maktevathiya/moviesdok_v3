from django import template
from datetime import datetime
import humanize  # Install using `pip install humanize`

register = template.Library()

@register.filter
def metric_format(value):
    """ Converts large numbers into metric notation (e.g., 1500000 -> "1.5M") """
    try:
        value = int(value)
        if value >= 1_000_000_000:
            return f"{value // 1_000_000_000}B" if value % 1_000_000_000 == 0 else f"{value / 1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"{value // 1_000_000}M" if value % 1_000_000 == 0 else f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value // 1_000}K" if value % 1_000 == 0 else f"{value / 1_000:.1f}K"
        return str(value)
    except (ValueError, TypeError):
        return value  # Return original value if not a number


@register.filter
def date_format(value):
    """ Converts a date string (YYYY-MM-DD) into a human-readable format """
    try:
        date_obj = datetime.strptime(value, "%Y-%m-%d").date()
        return date_obj.strftime("%d %b %Y")  # Returns format: Day, Month Year (e.g., 11, Feb 2022)
    except (ValueError, TypeError):
        return value  # Return original value if it's not a valid date
    


@register.filter
def time_format(value):
    """ Converts a number (in seconds) into a time format (HH:MM) """
    try:
        # Ensure the value is an integer
        total_minutes = int(value)
        
        # Calculate hours and minutes
        hours = total_minutes // 60  # Divide by 3600 to get hours
        minutes = total_minutes % 60  # Get remaining minutes

        # Format the time as HH:MM
        return f"{hours:02}hrs {minutes:02} min"

    except (ValueError, TypeError):
        return value  # Return the original value if not a valid number
