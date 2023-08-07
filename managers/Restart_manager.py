import asyncio
import time
import os
from managers import World_manager
from managers import Server_manager


class RestartManager:
    SAFE_SAVING_TIME = 60  # my world is 1k grids count

    def __init__(self, server):
        self.server = server
        self.world_manager = World_manager.WorldManager(server.get_save_path(), rw='w')

    async def delay_before_restart(self):
        if self.server.settings['do_server_use_depatch_savefix']:
            raise AttributeError('Program not support restart with depatch yet')
        return int(self.server.settings['restart_delay'])

    @staticmethod
    async def restart_if_depatch():  # IN PROGRES
        kogdasbs = int(save_fix.kogdasbs(RESTARTWATCH + 'Instance/Saves/VanillaHard/', 'Backup/'))
        for i in range(6):
            await toconsole(consoles,
                            [f'!say  \n ! \n REGULAR RESTART IN {kogdasbs // 60} MIN {kogdasbs % 60} SEK \n ! ',
                             f'!notify " RESTART IN {kogdasbs // 60} MIN {kogdasbs % 60} SEK " 5000 Red'])
            kogdasbs = kogdasbs // 2 + 1
            await asyncio.sleep(int(kogdasbs))
        await asyncio.sleep(15)  # надо удостовериться что в папке лежит sbs
        while save_fix.kogdasbs('C:/hard-serwer/Instance/Saves/VanillaHard/', 'Backup/') < kogdasbs:
            await asyncio.sleep(10)
        subprocess.call("TASKKILL /F /IM Torch.Server.exe", shell=True)

        # miss edit commands

        await asyncio.sleep(3)

    def when_depatch_make_sbs(self):  # IN PROGRES
        path = self.server.get_save_path()
        if os.path.exists(path + 'SANDBOX_0_0_0_.sbs'):
            return 1800 - (time.time() - int(os.path.getctime(path + 'SANDBOX_0_0_0_.sbs'))) % 3600
        else:
            for backup in reversed(self.server.get_backup_path_list()):
                if os.path.exists(backup + 'SANDBOX_0_0_0_.sbs'):
                    return 1800 - (time.time() - int(os.path.getctime(backup + 'SANDBOX_0_0_0_.sbs'))) % 3600

    @staticmethod
    def flip_plugins():  # IN PROGRES
        for plugin in [f for f in os.listdir(plugins['torch'] + 'PluginsStore/' + plugins['load']) if
                       os.path.isfile(os.path.join(plugins['torch'] + 'PluginsStore/' + plugins['load'], f))]:
            try:
                os.replace(plugins['torch'] + 'PluginsStore/' + plugin, plugins['torch'] + 'Plugins/' + plugin)
            except FileNotFoundError:
                pass
        for plugin in [f for f in os.listdir(plugins['torch'] + 'PluginsStore/' + plugins['unload']) if
                       os.path.isfile(os.path.join(plugins['torch'] + 'PluginsStore/' + plugins['unload'], f))]:
            try:
                os.replace(plugins['torch'] + 'Plugins/' + plugin, plugins['torch'] + 'PluginsStore/' + plugin)
            except FileNotFoundError:
                pass

        tmp = plugins['load']
        plugins['load'] = plugins['unload']
        plugins['unload'] = tmp
        print('флипнул плагины')


if __name__ == '__main__':
    server = Server_manager.Server('C:\\Users\\lena0\\OneDrive\\Рабочий стол\\test_server',
                                   {'do_server_use_depatch_savefix': True})
    restart_manager = RestartManager(server)
    print(restart_manager.delay_before_restart())
    print(restart_manager.when_depatch_make_sbs())
