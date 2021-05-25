from subprocess import run
import pytest

@pytest.fixture
def status():
    return ['systemctl','--user','status','-l','fossil.socket']

def test_fossile_service_running(status):
    x = run(status)
    assert x.returncode==0
