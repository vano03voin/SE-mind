import asyncio
import psutil
import os
from pprint import pprint
from datetime import datetime


class Server:
    """класс для создания обьекта сервера"""
    exePath = 'Torch.Server.exe'
    instancePath = 'Instance/'
    savePath = 'Saves/'
    backupsPath = 'Backup/'

    available_restart_prams = (
        'fix_world',
        'check_security'
    )

    def __init__(self, r_path: str, settings):
        print(f'start monitoring server {r_path}')
        self.root_path = self.fix_path(r_path)
        self.settings = settings
        self.work_status = True

    def turn_on(self):
        if not self.is_working():
            os.popen(self.root_path + self.exePath)
            self.work_status = True

    def turn_off(self):
        if pid := self.is_working():
            psutil.Process(pid).kill()
            self.work_status = False

    def get_save_path(self, backups=False):
        path = self.root_path+self.instancePath+self.savePath
        files = [f.name for f in os.scandir(path) if f.is_dir()]
        world_path = files[0]
        for file in files:
            if os.path.getmtime(path + file) > os.path.getmtime(path + world_path):
                world_path = file
        return path + world_path + '/' + ('Backup/' if backups else '')

    def get_backup_path_list(self):
        path = self.get_save_path(backups=True)
        return [(path+f.name+'/') for f in os.scandir(path) if f.is_dir()]

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
        if type(other) == Server:
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
