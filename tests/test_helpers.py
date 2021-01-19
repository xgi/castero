from castero import helpers


def test_third_zero():
    result = helpers.third(0)
    assert result == 0


def test_third_basic():
    result = helpers.third(3)
    assert result == 1


def test_third_indivisible():
    result = helpers.third(4)
    assert result == 1


def test_median_empty():
    values = []
    result = helpers.median(values)
    assert result is None


def test_median_1():
    values = [1]
    result = helpers.median(values)
    assert result == 1


def test_median_2():
    values = [1, 3]
    result = helpers.median(values)
    assert result == 2


def test_median_3():
    values = [1, 2, 3]
    result = helpers.median(values)
    assert result == 2


def test_sanitize_path_blank():
    path = ""
    result = helpers.sanitize_path(path)
    assert result == ""


def test_sanitize_path_0():
    path = "test"
    result = helpers.sanitize_path(path)
    assert result == "test"


def test_sanitize_path_1():
    path = "te%st"
    result = helpers.sanitize_path(path)
    assert result == "te_st"


def test_sanitize_path_hyphen():
    path = "te-st"
    result = helpers.sanitize_path(path)
    assert result == "te-st"


def test_sanitize_path_many():
    path = "!@#$%^&*()=+`~<>?/"';:'
    result = helpers.sanitize_path(path)
    assert result == "_" * len(path)


def test_seconds_to_time():
    seconds = (60 * 60) + (60 * 23) + 45
    result = helpers.seconds_to_time(seconds)
    assert result == "01:23:45"


def test_negative_seconds_to_time():
    result = helpers.seconds_to_time(-10)
    assert result == "00:00:00"


def test_is_true_yes():
    assert helpers.is_true('True')
    assert helpers.is_true('true')
    assert helpers.is_true('1')


def test_is_true_no():
    assert not helpers.is_true('False')
    assert not helpers.is_true('')
    assert not helpers.is_true('hi')
