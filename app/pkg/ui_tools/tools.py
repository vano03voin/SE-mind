import PySimpleGUI as sg
import configparser
import asyncio

from typing import Set, Tuple

from app.pkg.settings import Setting
from app.pkg.server_tools.tools import Server
from app.pkg.discord_tool.tools import SEDiscordBot
from app.pkg.snapshot_tool.tools import snapshots_loop


class MainWindow:
    """
        Main window where u can see all servers and can interact with them.
    """
    main_settings = (
        Setting('discord_tocken', str,
                'Discord bot tocken. DOUBLE CHECK u give him all Privileged Gateway Intents'),
        Setting('observe_silent_crash', bool,
                'Turn on server silent crash observing? (restart server to apply) (need wel setted discord bot above)'),
        Setting('observe_custom_restart', bool,
                'Let u use SE-mind server restart (need ds bot)'),
        Setting('send_backups_to_server', bool,
                'Let u use SE-analitics for building graphs from ur world data'),
        Setting('api_key', bool,
                'API key what u buy from vano03voin'))
    server_tool = ['Settings', 'Delete']

    def __init__(self, servers: Set[Server]):
        # Setup Servers
        self.servers = servers
        self.default_server_settings = Server.default_settings | {pram: '' for pram in Server.available_restart_prams}
        self.servers_config = configparser.ConfigParser(defaults=self.default_server_settings)
        self.startup_servers()

        # Setup App
        self.default_main_setting = {pram.name: '' for pram in self.main_settings}
        self.main_window_config = configparser.ConfigParser(defaults=self.default_main_setting)
        self.read_settings('main_settings.ini', self.main_window_config)
        self.save_settings('main_settings.ini', self.main_window_config)

        # Setup Discord
        self.startup_discord()

        self.window = sg.Window('SE-Mind monitoring', self.construct_main_window(), enable_close_attempted_event=True)

        event, values = self.window.read(timeout=100)

        # Setup snapshot sending
        api_key = self.main_window_config['DEFAULT']['send_backups_to_server']
        send_backups_to_server = self.main_window_config['DEFAULT']['send_backups_to_server']
        # if api_key and send_backups_to_server and False:
        #asyncio.create_task(snapshots_loop(servers=self.servers, api_key=api_key))
        snapshots_loop(servers=self.servers, api_key=api_key)

    def startup_servers(self):
        self.read_settings('servers.ini', self.servers_config)
        for server_path in self.servers_config.sections():
            try:
                self.servers.add(Server(server_path, self.servers_config[server_path]))
            except FileNotFoundError:
                print(f"Server from {self.servers_config[server_path]} not exist")

    def startup_discord(self):
        if self.main_window_config['DEFAULT']['discord_tocken'] != '':
            self.discord_bot = SEDiscordBot(self.servers)
            asyncio.create_task(self.discord_bot.start_bot(self.main_window_config))

    def construct_server_row(self, server: Server, size: tuple = (20, None)) -> list:
        return [sg.Text(server.root_path, size=size),
                sg.StatusBar(f'Work: {server.is_working()}', size=size),
                sg.ButtonMenu('Commands', ['', self.server_tool], key=server)]

    def construct_main_window(self, size: tuple = (20, None)):
        return [
            [sg.Column(layout=[[sg.Text('Main settings', size=size), sg.Text('', size=size), sg.Button('App settings')],
                               [sg.Text('Server', size=size), sg.Text('Status', size=size),
                                sg.Button('Add new exe of server')],
                               *[self.construct_server_row(server, size) for server in self.servers]], key='-servers')],
            ]
            #[sg.Output(size=(66, 10))]]

    async def run_window(self):
        while True:
            event, values = self.window.read(timeout=100)

            if event == 'Add new exe of server':
                filename = sg.popup_get_file('filename to open', no_window=True)
                if Server.exePath in filename:
                    filename = filename[:-len(Server.exePath)]
                    new_server = Server(filename, settings=self.default_server_settings)
                    if new_server not in self.servers:
                        self.servers.add(new_server)
                        self.servers_config[filename] = self.servers_config.defaults()
                        self.save_settings('servers.ini', self.servers_config)
                        self.window.extend_layout(self.window['-servers'], [self.construct_server_row(new_server)])
                    else:
                        sg.popup(f'Server {filename} already exist in my mind')
                else:
                    sg.popup(f'Incorrect file, select {Server.exePath}')

            if event in self.servers:
                match values[event]:
                    case 'Settings':
                        settings_w = ServerSettingsWindow(event)
                        asyncio.get_event_loop().create_task(settings_w.run_window())
                    case 'Delete':
                        if 'Yes' == sg.popup_yes_no('Remove server from monitoring?'):
                            self.servers.remove(event)
                            self.window.close()
                            self.window = sg.Window('SE-Mind monitoring', self.construct_main_window())

            if event == 'App settings':
                m_setting_w = MainWindowSettingsWindow(self.main_settings)
                asyncio.get_event_loop().create_task(m_setting_w.run_window())

            if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT and sg.popup_yes_no(
                    'Do you really want to exit?') == 'Yes':
                self.window.close()
                break

            if event == sg.WIN_CLOSED:
                self.window.close()
                break

            await asyncio.sleep(0)

    @staticmethod
    def save_settings(path: str, config: configparser.ConfigParser) -> None:
        with open(path, mode='w', encoding="utf-8") as configfile:  # "utf-8" 'cp1252'
            config.write(configfile)

    @staticmethod
    def read_settings(path: str, config: configparser.ConfigParser) -> None:
        try:
            with open(path, mode='r+', encoding="utf-8") as fp:
                config._read(fp, path)
        except:
            pass


class SettingWindowBase:
    @staticmethod
    def construct_setting_row(settings_list):
        zipped_data = list(zip(*settings_list))

        return [sg.Frame('Setting', [[sg.Text(text)] for text in zipped_data[0]]),
                sg.Frame('Descriprion', [[sg.Text(text)] for text in zipped_data[1]]),
                sg.Frame('Value type', [[sg.Text(text)] for text in zipped_data[2]])]


class MainWindowSettingsWindow(SettingWindowBase):
    def __init__(self, settings: Tuple[Setting, ...]):
        settings_tip_layout = [
            [sg.Text('1 In program folder open main_settings.ini')],
            [sg.Text('2 Find settings block whith [DEFAULT]')],
            [sg.Text('3 Reed below setting name, decription, value type, default value')],
            [sg.Text('4 Change settings what u need, save file, restart SE-mind to apply changes')],
            [sg.Text('DONT FORGET. IF U WANT MAKE SETTING (FALSE/NO/NONE) JUST LEAVE SETTING EMPTY')]]

        layout = [
            [sg.Button('Инструкция как получить токен бота и правильно настроить', key='get_ds_tocken_instruction')],
            [sg.Frame('Settings instruction', settings_tip_layout)],
            [sg.Frame('Discord settings', [self.construct_setting_row(settings)])]]

        self.window = sg.Window(f'Main settings', layout)

    async def run_window(self):
        while True:
            event, values = self.window.read(timeout=100)
            if event in (None, sg.WIN_CLOSED):
                self.window.close()
                break
            await asyncio.sleep(0)


class ServerSettingsWindow(SettingWindowBase):
    def __init__(self, server: Server):
        settings_tip_layout = [
            [sg.Text('1 In program folder open servers.ini')],
            [sg.Text(f'2 Find settings block whith [{server.root_path}]')],
            [sg.Text('3 Reed below setting name, decription, value type, default value')],
            [sg.Text('4 Change settings what u need, save file, restart SE-mind to apply changes')],
            [sg.Text('DONT FORGET. IF U WANT MAKE SETTING (FALSE/NO/NONE) JUST LEAVE SETTING EMPTY')]]

        discord_settings_layout = [
            [sg.Text('SETTINGS BELLOW WORK ONLY IF CORRECT DS TOCKEN IN MAIN SETTINGS')],
            [sg.Text('Double check that ur ds bot can reed and write in chanels below')],
            self.construct_setting_row(server.discord_settings)]

        restart_settings_layout = [
            [sg.Text('Works only with discord bridge')],
            self.construct_setting_row(server.restart_settings),
            [sg.Text('What i have to do due restart')],
            self.construct_setting_row(server.restart_tasks_settings)]

        layout = [
            [sg.Frame('Settings instruction', settings_tip_layout)],
            [sg.Frame('Discord settings', discord_settings_layout)],
            [sg.Frame('Restart settings', restart_settings_layout)]]

        self.window = sg.Window(f'Settings of {server.root_path}', layout)

    async def run_window(self):
        while True:
            event, values = self.window.read(timeout=100)
            if event in (None, sg.WIN_CLOSED):
                self.window.close()
                break
            await asyncio.sleep(0)
