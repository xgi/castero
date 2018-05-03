import requests
import os
from castero.datafile import DataFile
from castero.downloadqueue import DownloadQueue


def test_datafile_download():
    mydownloadqueue = DownloadQueue()
    urls = ["https://google.com", "https://bing.com", "https://amazon.com"]
    attempt = 0
    for url in urls:
        DataFile.download_to_file(url, "datafile_download_temp",
                                  "datafile download name", mydownloadqueue)
        r = requests.get(urls[attempt])
        if r.status_code == 200:
            break
    assert os.path.exists("datafile_download_temp")
    os.remove("datafile_download_temp")
