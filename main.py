import asyncio

from app.pkg.ui_tools.tools import MainWindow

SERVERS = set()  # It uses in every module of SE-mind

# Я в тысячный раз пытаюсь доделять это все до кондиции, но каждый раз возвращаясь через 2 месяца
# я обсолютно все забываю. 26.07.24 я пропитаю код коментариями в первую очередь для себя, чтобы не тратить время
# просто на то, чтобы понять, что этот код делает и что в нем работает, а что нет. Начнем.


async def main():
    main_window = MainWindow(SERVERS)  # Inicialization of all

    main_window_coro = asyncio.create_task(main_window.run_window())

    await main_window_coro

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
