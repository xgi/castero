from bs4 import BeautifulSoup
import re


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


def sanitize_path(path) -> str:
    """Replaces any characters in path that the file system may not support.

    This method replaces any non-alphanumeric characters with an underscore,
    with the exception of hyphens.

    Args:
        path: the original path

    Returns:
        str: the given path with potentially unsafe characters replaced
    """
    # adapted from https://stackoverflow.com/a/13593932
    path = re.sub('[^\w\-]', '_', path)
    return path


def is_true(string) -> bool:
    """Determines whether a string represents True.

    As the name suggests, any input which is not explicitly evaluated to True
    will cause this method to return False.

    Args:
        string: the string to evaluate
    """
    assert isinstance(string, str)

    return string in ['True', 'true', '1']


def html_to_plain(html) -> str:
    """Converts a potentially HTML-formatted string to user-friendly plaintext.
    
    Args:
        html: the text to convert with potential html tags

    Returns:
        str: the given text with html tags removed
    """
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()