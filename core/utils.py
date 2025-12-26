from datetime import datetime

def time_to_minutes(t:str) -> int:
    if not t:
        return 0
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

def get_month_year(param: str) -> tuple[int, int]:
    month, year = 0, 0
    if param:
        month = param[5:]
        year = param[:4]
    else:
        month = datetime.now().month
        year = datetime.now().year
    try:
        month = int(month)
        year = int(year)
        if month > 12 or month < 1:
            raise ValueError('Not valid month')
    except:
        month = datetime.now().month
        year = datetime.now().year

    return month, year


def sample_variance(data: list[int|float]) -> float:
    n = len(data)
    if n <= 1:
        return 0
    mean = sum(data)/n
    sq_sum = 0
    for val in data:
        sq_sum += (val-mean)**2
    
    return sq_sum/(n-1)

def min_to_time(min: float|int) -> str:
    min = round(min)
    hour = min//60
    mins = min%60
    return f'{"%02d" % hour}:{"%02d" % mins}'