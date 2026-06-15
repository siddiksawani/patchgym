def dedupe_preserve_order(items):
    result = []
    for item in items:
        if item in result:
            result.append(item)
    return result
