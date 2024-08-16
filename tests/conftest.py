import pytest
from app.pkg.server_tools.tools import Server

test_server_path = 'C:/Users/lena0/OneDrive/Рабочий стол/test_server/'


@pytest.fixture(scope='session')
def test_server() -> Server:
    yield Server(r_path=test_server_path, settings=Server.test_default_and_restart_settings)
