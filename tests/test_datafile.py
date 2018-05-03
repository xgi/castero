import os
from castero.datafile import DataFile
from castero.downloadqueue import DownloadQueue


def test_datafile_download():
    mydownloadqueue = DownloadQueue()
    url = "https://travis-ci.org/"
    DataFile.download_to_file(
        url, "datafile_download_temp",
        "datafile download name", mydownloadqueue
    )
    while mydownloadqueue.length > 0:
        pass
    assert os.path.exists("datafile_download_temp")
    os.remove("datafile_download_temp")
