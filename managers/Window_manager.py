import PySimpleGUI as sg
import asyncio
import time


class Window:
    def __init__(self, server):
        #sg.change_look_and_feel('DarkAmber')
        layout = [
            [sg.Text('Сервер упал или это ты его выключил?')],
            [sg.Text('', key='status')],
            [sg.Button('Это я его офнул. Отложи запуск на 2 мин')]
        ]

        self.window = sg.Window('Вопрос на милион..', layout, keep_on_top=True)
        self.server = server

    async def ui(self):
        start = time.time()
        while True:
            event, value = self.window.read(timeout=1)
            if (time.time() - start) > 10:
                print('seems like server down, i on it')
                self.window.close()
                try:
                    self.server.turn_on()
                except:
                    print(f'i tryed to up server but {_}')
                break
            if event in ('Это я его офнул. Отложи запуск на 2 мин', None, 'Cancel'):
                self.window.close()
                self.server.work_status = True
                break
            await asyncio.sleep(0)
