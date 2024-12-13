def filter_latency(data):
    """
    Processes data before it is displayed in the widget.
    Args:
        data (list): Raw data from the data provider.
    Returns:
        list: Processed data.
    """
    print("Processing data...custom_result_handler")
    return [item for item in data if item.get("latency", 0) < 100]
