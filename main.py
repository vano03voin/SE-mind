import asyncio

from loguru import logger

from app.pkg.ui_tools.tools import MainWindow
from app.pkg.snapshot_tool.tools import snapshots_loop

SERVERS = set()  # It uses in every module of SE-mind

# Я в тысячный раз пытаюсь доделять это все до кондиции, но каждый раз возвращаясь через 2 месяца
# я обсолютно все забываю. 26.07.24 я пропитаю код коментариями в первую очередь для себя, чтобы не тратить время
# просто на то, чтобы понять, что этот код делает и что в нем работает, а что нет. Начнем.


async def main():
    main_window = MainWindow(SERVERS)  # Inicialization of all

    logger.add(main_window.window["-OUTPUT-"].write, level="DEBUG", format="{time:HH:mm:ss} {function} {message}", filter=lambda record: record["level"].no < 40, enqueue=True)

    main_window_coro = asyncio.create_task(main_window.run_window())

    if main_window.api_key and main_window.main_window_config['DEFAULT']['send_backups_to_server']:
        asyncio.create_task(snapshots_loop(servers=SERVERS, api_key=main_window.api_key))

    await main_window_coro

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
