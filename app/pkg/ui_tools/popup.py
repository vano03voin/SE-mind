import PySimpleGUI as sg
import asyncio
import time

from app.pkg.server_tools.tools import Server


class Window:
    def __init__(self, server):
        self.server = server

        layout = [
            [sg.Text('Сервер упал или это ты его выключил?')],
            [sg.Text('')],
            [sg.Button('Dont up server in 4 min')]
        ]

        self.window = sg.Window('Вопрос на милион..', layout, keep_on_top=True)

    async def ui(self):
        start = time.time()
        while True:
            event, value = self.window.read(timeout=100)

            if (time.time() - start) > 10:
                print('seems like server down, i on it')
                self.window.close()
                try:
                    self.server.turn_on()
                except:
                    print(f'i tryed to up server but {_}')
                break

            if event in ('Dont up server in 4 min', None, 'Cancel'):
                self.window.close()
                self.server.work_status = True
                break
            await asyncio.sleep(0)
