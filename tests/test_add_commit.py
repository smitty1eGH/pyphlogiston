from dataclasses import dataclass
from pathlib import Path
from bs4 import BeautifulSoup as Bs
import requests
import pytest

@dataclass
class Requ:
    requestId: str
    command:   str
    authToken: str
    payload:   str
    indent:    int
    jsonp:     str


@dataclass
class Resp:
    fossil:    str
    requestId: str
    resultCode: str
    resultText: str
    payload: str
    timestamp: str
    payloadVersion: int
    command: str
    apiVersion: int
    warnings: str
    g: str
    procTimeMs: int

@pytest.fixture
def url():
    return 'http://127.0.0.1:9000/json/'

@pytest.fixture
def data_path():
    return '/home/osboxes/proj/pyphlogiston/pyphlogiston/data'

@pytest.fixture
def add_files0(data_path):
    p = Path(data_path)
    return [str(f) for f in p.glob('./*')]

def test_fossil_add(url,add_files0):
    u=f'{url}add'
    print(f'{u=}')
    r = requests.post(u)
    soup = Bs(r.text,'html.parser')
    #v = soup.find_all('div',class_='content')
    print(soup)
