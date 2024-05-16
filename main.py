import asyncio

from app.pkg.ui_tools.tools import MainWindow

SERVERS = set()


async def main():
    main_window = MainWindow(SERVERS)

    main_window_coro = asyncio.create_task(main_window.run_window())

    await main_window_coro

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
