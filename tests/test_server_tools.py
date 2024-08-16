from app.pkg.server_tools.tools import Server


class TestServer:
    @staticmethod
    def test_turn_on(test_server: Server):
        assert test_server.turn_on() is None

    @staticmethod
    def test_turn_off(test_server: Server):
        assert test_server.turn_off() is None

    @staticmethod
    def test_get_save_path(test_server: Server):
        assert type(test_server.get_save_path()) is str

    @staticmethod
    def test_get_backup_path_list(test_server: Server):
        assert type(test_server.get_backup_path_list()) is list
