import os
from unittest import mock

from castero.datafile import DataFile
from castero.downloadqueue import DownloadQueue


def test_datafile_download(display):
    display.change_status = mock.MagicMock(name="change_status")
    mydownloadqueue = DownloadQueue()
    url = "https://travis-ci.org/"
    DataFile.download_to_file(
        url,
        "datafile_download_temp",
        "datafile download name",
        mydownloadqueue,
        display=display
    )
    while mydownloadqueue.length > 0:
        pass
    assert display.change_status.call_count > 0
    assert os.path.exists("datafile_download_temp")
    os.remove("datafile_download_temp")


def test_datafile_download_bad_url(display):
    display.change_status = mock.MagicMock(name="change_status")
    mydownloadqueue = DownloadQueue()
    url = "https://bad"
    DataFile.download_to_file(
        url,
        "datafile_download_temp",
        "datafile download name",
        mydownloadqueue,
        display=display
    )
    while mydownloadqueue.length > 0:
        pass
    assert display.change_status.call_count > 0
    assert not os.path.exists("datafile_download_temp")
