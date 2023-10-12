import asyncio
import time
import os

from app.pkg.world_tools.tools import WorldManager
from app.pkg.server_tools.tools import Server


class RestartManager:
    SAFE_SAVING_TIME = 60  # my world is 1k grids count

    def __init__(self, server: Server, send_sms):
        self.send_sms = send_sms
        self.server = server
        self.world_manager = WorldManager(server.get_save_path(), rw='w')

    def delay_before_restart(self):
        if self.server.settings['is_depatch_saving']:
            raise AttributeError('Program not support restart with depatch yet')
        return int(self.server.settings['delay_before_restart'])

    async def do_restart(self):
        delay = self.delay_before_restart()
        for i in range(5):
            await self.send_sms([
                [self.server.settings['ingame_chat_id']],
                [f'!say  \n ! \n RESTART IN {delay // 60} MIN {delay % 60} SEK \n ! ',
                 f'!notify " RESTART IN {delay // 60} MIN {delay % 60} SEK " 5000 Red']])
            delay = delay // 2 + 1
            await asyncio.sleep(delay)
        await asyncio.sleep(delay)

        if self.server.settings['is_depatch_saving']:
            await self.send_sms([[self.server.settings['ingame_chat_id']],
                                 ['Say admin that restart dont work with depatch']])
        else:
            await self.send_sms([[self.server.settings['commands_chat_id']], ['!stop']])
            await asyncio.sleep(self.SAFE_SAVING_TIME)
        self.server.turn_off()
        try:
            self.world_manager.execute_commands(
                [self.server.settings[pram] for pram in self.server.available_restart_prams if self.server.settings[pram] != ''])
            del self.world_manager
        except:
            print('it often happends when SANDBOX_0_0_0.sbs dont exist')

        self.server.turn_on()
        while not self.server.is_b5_exist():
            await asyncio.sleep(20)
        await asyncio.sleep(10)
        self.server.turn_off()
        await asyncio.sleep(5)
        self.server.turn_on()

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

    def update_essential(self):  # IN PROGRES
        data = checkfile('modules/save_tools/per_restart/hard-serwer/Essentials/motd/motd.txt')
        news = checkfile('modules/save_tools/per_restart/hard-serwer/Essentials/motd/{news}.txt')
        data = data.replace('{today}', str(datetime.today())[:10])
        data = data.replace('{news}', news)
        tree = ET.parse('C:/hard-serwer/Instance/Essentials.cfg')
        save = tree.getroot()
        save.find('Motd').text = data
        tree.write('C:/hard-serwer/Instance/Essentials.cfg', xml_declaration=True)
