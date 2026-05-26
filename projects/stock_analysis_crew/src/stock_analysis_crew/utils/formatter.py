"""
Formatter — Indian number formatting and report formatting helpers.
"""


def format_indian_number(number) -> str:
    """
    Format a number in Indian numbering system (lakh, crore).

    Examples:
        1234567 -> "12,34,567"
        1500000000 -> "150,00,00,000" (150 crore)
    """
    if number is None or number == "N/A":
        return "N/A"

    try:
        number = float(number)
    except (ValueError, TypeError):
        return str(number)

    if number < 0:
        return "-" + format_indian_number(-number)

    # Convert to integer for formatting
    num_str = str(int(number))

    if len(num_str) <= 3:
        return num_str

    # Last 3 digits
    last_three = num_str[-3:]
    remaining = num_str[:-3]

    # Group remaining digits in pairs
    groups = []
    while remaining:
        groups.insert(0, remaining[-2:])
        remaining = remaining[:-2]

    return ",".join(groups) + "," + last_three


def format_indian_currency(number) -> str:
    """
    Format a number as Indian Rupees with lakh/crore notation.

    Examples:
        1500000 -> "₹15.00 Lakh"
        150000000 -> "₹15.00 Crore"
        1900000000000 -> "₹19.00 Lakh Crore"
    """
    if number is None or number == "N/A":
        return "N/A"

    try:
        number = float(number)
    except (ValueError, TypeError):
        return str(number)

    if number < 0:
        return "-" + format_indian_currency(-number)

    if number >= 1e12:  # Lakh Crore
        return f"₹{number / 1e12:.2f} Lakh Crore"
    elif number >= 1e7:  # Crore
        return f"₹{number / 1e7:.2f} Crore"
    elif number >= 1e5:  # Lakh
        return f"₹{number / 1e5:.2f} Lakh"
    else:
        return f"₹{format_indian_number(number)}"


def format_percentage(value) -> str:
    """Format a decimal as percentage string."""
    if value is None or value == "N/A":
        return "N/A"

    try:
        value = float(value)
        return f"{value * 100:.2f}%" if abs(value) < 1 else f"{value:.2f}%"
    except (ValueError, TypeError):
        return str(value)


def format_large_number(number) -> str:
    """
    Format a large number with appropriate suffix (K, L, Cr).
    Useful for volume formatting.
    """
    if number is None or number == "N/A":
        return "N/A"

    try:
        number = float(number)
    except (ValueError, TypeError):
        return str(number)

    if number >= 1e7:
        return f"{number / 1e7:.2f} Cr"
    elif number >= 1e5:
        return f"{number / 1e5:.2f} L"
    elif number >= 1e3:
        return f"{number / 1e3:.1f}K"
    else:
        return str(int(number))
