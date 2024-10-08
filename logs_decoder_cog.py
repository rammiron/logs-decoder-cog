import os

import discord
import base64
from discord.ext import commands

if "cogs" in __name__:
    from .utils.rsa import decrypt
else:
    from utils.rsa import decrypt


class LogsCheckerCog(commands.Cog):
    exe_path = os.path.join(os.path.dirname(__file__), "logs-checker", 'logs-checker.exe')

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    def parse_logs(self, data: str):
        data_dict = {}
        event = ""
        index = 0.1
        for line in data.splitlines():
            split = line.strip("   ").split(":", maxsplit=1)
            if len(split) == 0:
                continue
            if split[0].startswith("Event["):
                if split[0] in data_dict.keys():
                    event = f"Event[{index}]"
                    data_dict[event] = {}
                    index += 1
                    continue
                event = split[0]
                data_dict[event] = {}
                continue

            if (split[0].startswith("Предыдущее завершение работы системы") or
                    split[0].startswith("Система перезагрузилась") and event != ""):
                data_dict[event]["Description"] = split[0] + ":" + split[1]
            if event != "":
                if len(split) > 1:
                    data_dict[event][split[0]] = split[1]
        return data_dict

    @commands.slash_command(name="help_win_logs", description="Помощь с логами Windows.")
    async def help_win_logs(self, ctx: discord.ApplicationContext):
        file = discord.File(self.exe_path)
        await ctx.respond("Здравствуйте. Чтобы Вас разбанили, "
                          "необходимо предоставить информацию,"
                          " что Вы отключились действительно по независящим от Вас причинам. "
                          "Просим предоставить логи Windows. Вы можете сделать это самостоятельно, "
                          "предоставив скриншоты с ошибками 6008, 41 из журнала Windows,  либо же запустить файл, "
                          "который соберет логи за Вас самостоятельно. "
                          "Сам файл разработан нашими программистами,"
                          " не содержит вирусов, "
                          "но для большей уверенности проверен на вирусы с помощью сервиса virustotal.\n"
                          "-> [ТЫК](https://www.virustotal.com/gui/file/"
                          "1c9bd2586f8bc2ffd4eb01e46a2462bc1ec3bce25bca9247aa882e347d75b13e)"
                          "\n"
                          "Просим отправить в этот чат сгенерированный файл.")
        await ctx.channel.send("Файл: ", file=file)

    @commands.message_command(name="Получить и обработать логи.", descriprion="Прочесть логи.")
    async def read_logs(self, ctx: discord.ApplicationContext, message: discord.Message):

        if not message.attachments:
            await ctx.respond("Файл logs.ds не обнаружен.", ephemeral=True)
            return
        attachment = message.attachments[0]

        if not attachment.filename.endswith(".ds"):
            return
        file = await attachment.read()
        decoded_from_base64 = base64.b64decode(file).decode()
        decrypted_from_rsa = decrypt(decoded_from_base64)
        parsed_logs = self.parse_logs(decrypted_from_rsa)
        if len(parsed_logs) < 1:
            await ctx.channel.send("Завершений работы с ошибкой не обнаружено.")
            return

        embed = discord.Embed(
            title="Логи завершения работы.",
            colour=discord.Colour.red()

        )
        for log in parsed_logs:
            embed.add_field(name=f"{log}:", value=f"Описание: {parsed_logs[log]['Description']}\nДата: "
                                                  f"{parsed_logs[log]['Date']}"
                                                  f" \nКод: {parsed_logs[log]['Event ID']}\n", inline=False)

        try:
            await ctx.respond("Успешно. Логи отправлены в личные сообщения.", ephemeral=True)
            await ctx.author.send(embed=embed)
        except:
            await ctx.channel.send(f"{ctx.author.mention}, похоже у вас закрыт лс. Откройте лс и повторите попытку.")
