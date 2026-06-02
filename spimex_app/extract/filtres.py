from datetime import datetime, date


def compare_date(tag, date_target: date):
    date_str: str = tag.find("span").text
    try:
        date_obj: date = datetime.strptime(date_str, "%d.%m.%Y").date()
        if date_obj > date_target:
            return True
    except (TypeError, ValueError):
        return False


def tag_filter(tag) -> bool:
    date_target: date = datetime(2023, 1, 1).date()

    if tag.name == "div" and "accordeon-inner__item" in tag.get("class", []):
        return compare_date(tag, date_target)
    return False
