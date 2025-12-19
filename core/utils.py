def time_to_minutes(t:str) -> int:
    if not t:
        return None
    h, m = map(int, t.split(":"))
    return h * 60 + m

def min_to_hrs(min: int):
    return min/60.0

def get_month_name(month: int) -> list[str] | None:
    dct_month = {
        1: ['jan', 'january'],
        2: ['feb', 'febuary'],
        3: ['mar', 'march'],
        4: ['apr', 'april'],
        5: ['may', 'may'],
        6: ['jun', 'june'],
        7: ['jul', 'july'],
        8: ['aug', 'august'],
        9: ['sep', 'september'],
        10: ['oct', 'october'],
        11: ['nov', 'november'],
        12: ['dec', 'december'],
    }
    if month not in dct_month:
        return None
    return dct_month[month]