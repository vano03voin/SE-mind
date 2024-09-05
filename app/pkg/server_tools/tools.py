import psutil
import os
from typing import List
from copy import deepcopy
from pprint import pprint
from app.pkg.settings import Setting


class Server:
    """класс для создания обьекта сервера"""
    exePath = 'Torch.Server.exe'
    instancePath = 'Instance/'
    savePath = 'Saves/'
    backupsPath = 'Backup/'

    base_settings = (
        Setting('server_name', str,
                'Alias for understending who is who. Format: test_server'),
        Setting('send_server_saves_to_server', bool,
                'If u set in main settings correct api_tocken, saves will send on server to analis'),)

    discord_settings = (
        Setting('use_discord_bridge', bool,
                'This server have and use discord bridge plugin? (first setup discord bot)'),
        Setting('stat_chat_id', int,
                'Private admin chat where we will publish stat of server'),
        Setting('log_chat_id', int,
                'Loging chat id'),
        Setting('commands_chat_id', int,
                'Commands chat id'),
        Setting('ingame_chat_id', int,
                'Ingame chat id'))

    restart_settings = (
        Setting('use_custom_restart', bool,
                'Turn on custom restarts, use only if u need our custom restart features(settings below)'),
        Setting('delay_before_restart', int,
                'Delay before restart in sekonds. default: 600'),
        Setting('is_depatch_saving', bool,
                'Do this server use depatch saving? DONT USE CUSTOM RESTART WHITH ENABLED DEPATCH SAVING'),
        Setting('restart_times', str,
                'When custom restart be in 24 format, here restart be in 02.00 and in 10.00. default: 2,10'))

    restart_tasks_settings = (
        Setting('fix_world', bool,
                'fix green signals in world'),
        Setting('check_security', bool,
                'check infinity cargo in world'))

    default_settings = {setting.name: '' for setting in (*base_settings, *discord_settings, *restart_settings, *restart_tasks_settings)}
    available_restart_prams = (setting.name for setting in restart_tasks_settings)
    test_default_and_restart_settings = deepcopy(default_settings) | {pram: '' for pram in available_restart_prams}

    def __init__(self, r_path: str, settings):
        print(f'start monitoring server {r_path}')
        self.root_path = self.fix_path(r_path)
        # get world id
        # world_file = ElementTree(self.get_save_path() + 'Sandbox.sbc')
        # sector = world_file.tree.getroot()
        # self.world_id = sector.find('WorldId').text

        self.settings = deepcopy(settings)
        self.work_status = True

    def turn_on(self):
        if not self.is_working():
            os.popen(self.root_path + self.exePath)
            self.work_status = True

    def turn_off(self):
        if pid := self.is_working():
            psutil.Process(pid).kill()
            self.work_status = False

    def get_save_path(self, backups=False) -> str:
        path = self.root_path + self.instancePath + self.savePath
        files = [f.name for f in os.scandir(path) if f.is_dir()]
        world_path = files[0]
        for file in files:
            if os.path.getmtime(path + file) > os.path.getmtime(path + world_path):
                world_path = file
        return path + world_path + '/' + ('Backup/' if backups else '')

    def get_backup_path_list(self) -> List[str]:
        path = self.get_save_path(backups=True)
        return [(path + f.name + '/') for f in os.scandir(path) if f.is_dir()]

    def is_working(self):
        path = self.fix_path(self.root_path)
        for proc in psutil.process_iter():
            try:
                if path in proc.exe().replace('\\', '/'):
                    return proc.pid
            except psutil.AccessDenied:
                pass
        return False

    def is_b5_exist(self):
        path = self.get_save_path() + 'SANDBOX_0_0_0_.sbsB5'
        if os.path.exists(path) and int(os.path.getsize(path)) > 10:
            return True
        return False

    def __eq__(self, other):
        if type(other) is Server:
            return self.root_path == other.root_path

    def __hash__(self):
        return hash(self.root_path)

    @classmethod
    def fix_path(cls, path_to_fix):
        path_to_fix.replace('\\', '/')
        path_to_fix.replace('//', '/')
        return path_to_fix if path_to_fix[-1] == '/' else path_to_fix + '/'


if __name__ == "__main__":
    server = Server('C:\\Users\\lena0\\OneDrive\\Рабочий стол\\test_server', [])
    pprint(server.get_backup_path_list())
