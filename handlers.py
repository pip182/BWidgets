def filter_latency(data):
    """
    Processes data before it is displayed in the widget.
    Args:
        data (list): Raw data from the data provider.
    Returns:
        list: Processed data.
    """
    if isinstance(data, list):
        data = [round(item * 1000, 2) for item in data if item.get("latency", 0) < 100]
    else:
        data = round(data * 1000, 2)
    print("Processing data...filter_latency", data)
    return data


def table_data(data):
    """
    Processes data before it is displayed in the widget.
    Args:
        data (list): Raw data from the data provider.
    Returns:
        list: Processed data.
    """
    print("Processing data...table_data", data)
    if isinstance(data, list):
        return [item for item in data if item.get("latency", 0) >= 0]
    else:
        return data
