import asyncio

from telegram import Update, Message
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from src.agent import LangGraphAgent


class TelegramBot:
    def __init__(self, tele_config, llm_config):
        self.tele_config = tele_config
        self.agent = LangGraphAgent(llm_config)
        print()

    def command(self):
        return [
            CommandHandler('start', "<something>"), # TODO: implement command function
            CommandHandler('help', "<something>")
        ]
    
    # async def response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     user_text = update.message.text
    #     chat_id = update.effective_chat.id
        
    #     reply = self.agent.invoke(user_text)
    #     await update.message.reply_text(reply)

    async def response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        chat_id = update.effective_chat.id

        history = context.bot_data.setdefault(chat_id, [])
        history.append({"role": "user", "content": user_text})

        sent = await update.message.reply_text("...")
        responses = await self._stream_reply(sent, history)

        history.append({"role": "assistant", "content": responses})

    async def _stream_reply(self, message: Message, history: list) -> str:
        # TODO: Edit streaming
        buffer = ""
        last_edit = ""
        last_edit_time = 0.0

        async for chunk in self.agent.astream(history):
            buffer += chunk
            now = asyncio.get_event_loop().time()

            # Edit only if content changed and enough time has passed
            if buffer != last_edit and (now - last_edit_time) >= 0.5:
                try:
                    await message.edit_text(buffer)
                    last_edit = buffer
                    last_edit_time = now
                except Exception:
                    pass  # ignore transient Telegram API errors

        # Final edit to ensure the complete text is shown
        if buffer != last_edit:
            try:
                await message.edit_text(buffer)
            except Exception:
                pass

        return buffer


    def run(self):
        application = ApplicationBuilder().token(self.tele_config["token"]).build()

        # Add commands
        commands = self.command()
        for command in commands:
            application.add_handler(command)

        # Add llm response
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.response))
        application.run_polling()
