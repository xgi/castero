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
