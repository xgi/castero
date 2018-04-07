def third(n) -> int:
    """Calculates one-third of a given value.

    Args:
        n: the integer to calculate one-third of

    Returns:
        int: one-third of n, rounded down
    """
    return int(n / 3)


def median(arr):
    """Determines the median of a list of numbers.

    Args:
        arr: a list of ints and/or floats of which to determine the median

    Returns:
        int or float: the median value in arr
    """
    if len(arr) == 0:
        return None

    arr_sorted = sorted(arr)
    midpoint = int(len(arr) / 2)

    if len(arr) % 2 == 0:
        # even number of elements; get the average of the middle two
        result = (arr_sorted[midpoint - 1] + arr_sorted[midpoint]) / 2
    else:
        result = arr_sorted[midpoint]
    return result
