from unittest import mock

from castero.__main__ import redirect_stderr


def test_redirect_stderr_returns_fd():
    with mock.patch("os.dup2"), mock.patch("os.fdopen"):
        fd = redirect_stderr()
        assert isinstance(fd, int)
        assert fd >= 0


def test_redirect_stderr_windows_skips_cdll():
    with mock.patch("os.name", "nt"), mock.patch("ctypes.CDLL") as mock_cdll, \
            mock.patch("os.dup2"), mock.patch("os.fdopen"):
        fd = redirect_stderr()
        assert isinstance(fd, int)
        mock_cdll.assert_not_called()


def test_redirect_stderr_posix_calls_cdll():
    with mock.patch("os.name", "posix"), \
            mock.patch("ctypes.CDLL") as mock_cdll, \
            mock.patch("os.dup2"), mock.patch("os.fdopen"):
        mock_libc = mock.MagicMock()
        mock_cdll.return_value = mock_libc
        with mock.patch("ctypes.c_void_p.in_dll") as mock_in_dll:
            mock_in_dll.return_value = mock.MagicMock()
            fd = redirect_stderr()
            assert isinstance(fd, int)
            mock_cdll.assert_called_once_with(None)
            assert mock_libc.fflush.called


def test_redirect_stderr_handles_typeerror():
    err = TypeError("argument of type 'NoneType' is not iterable")
    with mock.patch("os.name", "posix"), \
            mock.patch("ctypes.CDLL", side_effect=err), \
            mock.patch("os.dup2"), mock.patch("os.fdopen"):
        fd = redirect_stderr()
        assert isinstance(fd, int)
