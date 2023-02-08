import os
import sys
import openai
import logging
import time
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import telebot

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_TO_LOG = os.path.join(BASE_DIR, 'chat_bot.log')

rf_handler = RotatingFileHandler(PATH_TO_LOG, maxBytes=500000, backupCount=5)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s',
    handlers=[logging.StreamHandler(), rf_handler])

try:
    OPEN_API_KEY = os.environ['OPEN_API_KEY']
    TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
    CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
    print(TELEGRAM_TOKEN)

except KeyError as e:
    token_error = f'Ошибка с ТОКЕН {e}.'
    logging.error(token_error)
    sys.exit('sys.exit - Не получены ТОКЕН')

openai.api_key = OPEN_API_KEY

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def send_message(chat_id=CHAT_ID, message="Problem in ChatGPT"):
    """
    Функция отправляет сообщение через БОТ и логирует его.
    """
    logging.info(f'Сообщение << {message} >> отправлено в чат')
    return bot.send_message(chat_id, message)


def main():
    logging.info('Бот запущен')
    while True:
        try:
            @bot.message_handler(func=lambda _: True)  # '_' means variable but not used
            def handle_message(message):
                logging.info(message.text)
                try:
                    response = openai.Completion.create(
                        model="text-davinci-003",
                        prompt=message.text,
                        temperature=0.5,
                        max_tokens=1000,
                        top_p=1.0,
                        frequency_penalty=0.5,
                        presence_penalty=0.0,
                        stop=["You:"]
                    )
                    # print(response["choices"][0]["text"])
                    send_message(message.chat.id, response["choices"][0]["text"])
                except Exception as e:
                    net_error = f'ChatGPT do not response: {e}.'
                    logging.error(net_error)
                    send_message(message.chat.id, net_error)

            bot.polling()
        except Exception as e:
            bot_error = f'Бот упал с ошибкой: {e}'
            logging.error(bot_error)
            send_message(bot_error)
            time.sleep(60)  # увеличил интервал сообщений до 60 сек


if __name__ == '__main__':
    main()
