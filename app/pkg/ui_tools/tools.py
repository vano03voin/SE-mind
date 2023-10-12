import PySimpleGUI as sg
import configparser
import asyncio
import time

from typing import List, Optional

from app.pkg.server_tools.tools import Server
from app.pkg.discord_tool.tools import SEDiscordBot


class WindowBase:
    size = (20, None)

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


class MainWindow(WindowBase):
    """
        Main window where u can see all servers and can interact with them.
    """

    def __init__(self, servers: set):
        self.servers = servers
        self.server_tool = [
            'Settings',
            'Delete'
        ]

        self.default_server_settings = {
            'use_discord_bridge': '',  # bool
            'log_chat_id': '',  # int
            'commands_chat_id': '',  # int
            'ingame_chat_id': '',  # int
            'use_custom_restart': '',  # bool
            'delay_before_restart': '600',  # int
            'is_depatch_saving': '',  # bool
            'restart_times': '2,10',  # str
        } | {pram: '' for pram in Server.available_restart_prams}

        self.servers_config = configparser.ConfigParser(defaults=self.default_server_settings)
        self.read_settings('servers.ini', self.servers_config)
        for server_path in self.servers_config.sections():
            self.servers.add(Server(server_path, self.servers_config[server_path]))

        self.default_main_setting = {
            'discord_tocken': 'None'
        }

        self.main_window_config = configparser.ConfigParser(defaults=self.default_main_setting)
        self.read_settings('main_settings.ini', self.main_window_config)
        if self.main_window_config['DEFAULT']['discord_tocken'] == 'None':
            tocken = sg.popup_get_text('Discord bot tocken\nDOUBLE CHECK u give him all Privileged Gateway Intents')
            self.main_window_config['DEFAULT']['discord_tocken'] = tocken
        self.save_settings('main_settings.ini', self.main_window_config)
        self.discord_bot = SEDiscordBot(self.servers)
        asyncio.create_task(self.discord_bot.start_bot(self.main_window_config['DEFAULT']['discord_tocken']))

        self.window = sg.Window('SE-Mind monitoring', self.construct_main_window(), enable_close_attempted_event=True)

    def construct_server_row(self, server: Server, size: tuple) -> list:
        return [sg.Text(server.root_path, size=size),
                sg.StatusBar(f'Work: {server.is_working()}', size=size),
                sg.ButtonMenu('Commands', ['', self.server_tool], key=server)]

    def construct_main_window(self):
        size = self.size
        layout = [[
            sg.Text('Server', size=size), sg.Text('Status', size=size), sg.Button('Add new exe of server')
        ]]
        for server in self.servers:
            layout.append(self.construct_server_row(server, size))
        return layout

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
                        self.window.extend_layout(self.window, [self.construct_server_row(new_server, self.size)])
                    else:
                        sg.popup(f'Server {filename} already exist in my mind')
                else:
                    sg.popup(f'Incorrect file, select {Server.exePath}')

            if event in self.servers:
                match values[event]:
                    case 'Settings':
                        settings_w = ServerSettingsWindow(event)
                        asyncio.get_event_loop().create_task(settings_w.run_window(self.default_server_settings))
                    case 'Delete':
                        if 'Yes' == sg.popup_yes_no('Remove server from monitoring?'):
                            self.servers.remove(event)
                            self.window.close()
                            self.window = sg.Window('SE-Mind monitoring', self.construct_main_window())

            if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT and sg.popup_yes_no(
                    'Do you really want to exit?') == 'Yes':
                self.window.close()
                break

            if event == sg.WIN_CLOSED:
                self.window.close()
                break

            await asyncio.sleep(0)


class ServerSettingsWindow(WindowBase):
    """
        Window with settings of 1 server.
    """

    def __init__(self, server: Server):
        self.server = server
        size = self.size

        discord_settings = [
            [sg.Text('Server use discord bridge?', size=size), sg.Checkbox('Yes/No', key='use_discord_bridge')],
            [sg.Text('Double check that bot can reed and write in those chanels')],
            [sg.Text('Loging chat id', size=size), sg.Input('', key='log_chat_id')],
            [sg.Text('Commands chat id', size=size), sg.Input('', key='commands_chat_id')],
            [sg.Text('Ingame chat id', size=size), sg.Input('', key='ingame_chat_id')]
        ]

        awalible_commands = [
            ['fix_world', 'fix green signals in world'],
            ['check_security', 'check infinity cargo in world']
        ]
        commands_lst = [[sg.Checkbox(com[0], key=com[0], size=size), sg.Text(com[1])] for com in awalible_commands]

        restart_settings = [
            [sg.Text('(Works only with discord bridge)')],
            [sg.Text('Turn On custom restarts?', size=size), sg.Checkbox('Yes/No', key='use_custom_restart')],
            [sg.Text('Delay before restart in sekonds', size=size), sg.Input('', key='delay_before_restart')],
            [sg.Text('Do server use depatch saving?', size=size), sg.Checkbox('Yes/No', key='is_depatch_saving')],
            [sg.Text('When custom restart be in 24 format, here restart be in 02.00 and in 10.00', size=size),
             sg.Input('', key='restart_times')],
            [sg.Frame('What i have to do due restart', commands_lst)]
        ]

        layout1 = [
            [sg.Frame('Discord settings', discord_settings)],
            [sg.Frame('Restart settings', restart_settings)]
        ]

        layout2 = [
            []
        ]

        layout = [
            #[sg.Text('DONT FORGET THAT EVERY TEXT HAVE TOOLTIP WHERE U CAN REED INFO')],
            #[sg.Text('Just mount your mouse on name of setting')],
            [sg.Col(layout1, p=0), sg.Col(layout2, p=0)],
            [sg.Button('Save')]
        ]

        self.server_config = configparser.ConfigParser()
        self.read_settings('servers.ini', self.server_config)

        self.window = sg.Window(f'Settings of {server.root_path}', layout)

    async def run_window(self, default_server_settings: dict):
        self.window.read(timeout=100)
        for key, value in self.server_config[self.server.root_path].items():
            self.window[key].update(value)

        while True:
            event, values = self.window.read(timeout=100)
            if event in (None, sg.WIN_CLOSED):
                self.window.close()
                break

            if event == 'Save':
                for key in values:
                    if key in default_server_settings:
                        self.server.settings[key] = '' if values[key] is False else str(values[key])
                self.server_config[self.server.root_path] = self.server.settings
                self.save_settings('servers.ini', self.server_config)

            await asyncio.sleep(0)


if __name__ == '__main__':
    pass
