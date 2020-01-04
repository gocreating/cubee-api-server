def to_seconds(datetime):
    if not datetime:
        return -1
    return int(datetime.timestamp())
