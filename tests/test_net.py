from unittest import mock


from castero.net import Net


@mock.patch("requests.get")
def test_net_get_empty(get):
    Net.Get()
    assert get.called


@mock.patch("requests.get")
def test_net_get_uses_args(get):
    arg1 = "arg1"
    arg2 = "arg2"
    kwarg1 = "kwarg1"
    kwarg2 = "kwarg2"
    kwarg3 = "kwarg3"

    Net.Get(arg1, arg2, kwarg1=kwarg1, kwarg2=kwarg2, kwarg3=kwarg3)
    args, kwargs = get.call_args
    assert "arg1" in args
    assert "arg2" in args
    assert "kwarg1" in kwargs
    assert "kwarg2" in kwargs
    assert "kwarg3" in kwargs


@mock.patch("grequests.get")
def test_net_gget_empty(get):
    Net.GGet()
    assert get.called


@mock.patch("grequests.get")
def test_net_gget_uses_args(get):
    arg1 = "arg1"
    arg2 = "arg2"
    kwarg1 = "kwarg1"
    kwarg2 = "kwarg2"
    kwarg3 = "kwarg3"

    Net.GGet(arg1, arg2, kwarg1=kwarg1, kwarg2=kwarg2, kwarg3=kwarg3)
    args, kwargs = get.call_args
    assert "arg1" in args
    assert "arg2" in args
    assert "kwarg1" in kwargs
    assert "kwarg2" in kwargs
    assert "kwarg3" in kwargs
