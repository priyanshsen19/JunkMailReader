def parse_internal_date(internal_date_str):
    try:
        ms = int(internal_date_str)
        return ms // 1000
    except Exception:
        return None

def header_value(headers, name):
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value")
    return ""
