from decimal import Decimal


def money(value) -> str:
    return f"{Decimal(str(value or 0)):,.2f}"
