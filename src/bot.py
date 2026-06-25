from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler


class TelegramBot:
    def __init__(self, config):
        self.config = config

    def command(self):
        return [
            CommandHandler('start', "<something>"), # TODO: implement command function
            CommandHandler('help', "<something>")
        ]
    
    def generate(self, user_input):
        # TODO: integrate LLM
        # Currently just a template
        normalized_input: str = user_input.lower()

        if 'hi' in normalized_input:
            return 'Hello!'

        if 'how are you doing' in normalized_input:
            return 'I am functioning properly!'

        if 'i would like to subscribe' in normalized_input:
            return 'Sure go ahead!'

        return 'I didn’t catch that, could you please rephrase?'


    def run(self):
        application = ApplicationBuilder().token(self.config["tele_token"]).build()

        # Add commands
        commands = self.command()
        for command in commands:
            application.add_handler(command)
        
        application.run_polling()
