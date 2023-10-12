from discord.ext import tasks, commands


class MailCheckCog(commands.Cog):
    def __init__(self):
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=1)
    async def mail_check_loop(self):
        print('проверил почту')
        while MAIL_STORAGE:
            message = MAIL_STORAGE.pop(0)
            await msg_to_chanel(message[0], message[1])
