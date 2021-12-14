from bs4 import BeautifulSoup
import requests
from subprocess import run
import pytest


@pytest.fixture
def status():
    return ["systemctl", "--user", "status", "-l", "fossil.service"]


@pytest.mark.skip
def test_fossil_service_running(status):
    x = run(status)
    assert x.returncode == 0


@pytest.mark.skip
def test_fossil_version():
    r = requests.get("http://127.0.0.1:9000/version?verbose")
    soup = BeautifulSoup(r.text, "html.parser")
    v = soup.find_all("div", class_="content")
    print(v)
