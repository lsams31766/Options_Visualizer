#utilitis.py
from datetime import date, datetime

def days_until_date(target_date):
    """
    Calculates the number of days from today until a given target date.

    Args:
        target_year (int): The year of the target date.
        target_month (int): The month of the target date.
        target_day (int): The day of the target date.

    Returns:
        int: The number of days until the target date.
             Returns a positive integer if the date is in the future,
             a negative integer if the date is in the past,
             and 0 if the target date is today.
    """
    format_string = "%Y-%m-%d"
    # Convert the string to a datetime object
    datetime_target_date = datetime.strptime(target_date, format_string)

    today = date.today()
    
    time_difference = datetime_target_date.date() - today
    return time_difference.days
