import telegram



def send_message(bot, chat_id, msg):
    bot.sendMessage(chat_id=chat_id, text=msg)
