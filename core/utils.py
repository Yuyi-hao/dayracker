def time_to_minutes(t):
    if not t:
        return None
    h, m = map(int, t.split(":"))
    return h * 60 + m