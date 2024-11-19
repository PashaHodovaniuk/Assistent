from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import logging
import os

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота, полученный от BotFather
TOKEN = os.getenv("TOKEN")

# Токен для WeatherAPI (получите на https://www.weatherapi.com/)
API_KEY = os.getenv("API_KEY")

# Разрешённые идентификаторы тем
ALLOWED_TOPICS = [100, 12]  # Замените на реальные идентификаторы тем

# Включение логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция для обработки команды /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет! Я Ваш личный Ассистент! Пока могу сообщить погоду на сегодня и завтра.')

# Функция для обработки команды /weather_today
async def weather_today(update: Update, context: CallbackContext) -> None:
    city = 'Kryvyi Rih'  # Замените на ваш город
    country = 'UA'  # Замените на вашу страну

    try:
        url = f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city},{country}&lang=ru'
        response = requests.get(url)
        data = response.json()

        if 'error' in data:
            await update.message.reply_text(f"Произошла ошибка: {data['error']['message']}")
        else:
            current = data['current']
            temperature = current['temp_c']
            condition = current['condition']['text']
            wind_speed = current['wind_kph']

            message = f'\nТекущая погода:  {condition}.\n\nТемпература {temperature}°C.\n\nВетер {wind_speed} км/ч.'
            await update.message.reply_text(message)

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Произошла ошибка при запросе погоды: {e}")

# Функция для обработки команды /weather_tomorrow
async def weather_tomorrow(update: Update, context: CallbackContext) -> None:
    city = 'Kryvyi Rih'  # Замените на ваш город
    country = 'UA'  # Замените на вашу страну

    try:
        url = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city},{country}&days=2&lang=ru'
        response = requests.get(url)
        data = response.json()

        if 'error' in data:
            await update.message.reply_text(f"Произошла ошибка: {data['error']['message']}")
        else:
            forecast_day = data['forecast']['forecastday'][1]  # берем прогноз на завтра (индекс 1)
            day = forecast_day['day']
            temperature = day['avgtemp_c']
            condition = day['condition']['text']
            max_wind_speed = day['maxwind_kph']

            message = f'\nЗавтра погода:  {condition}.\n\nСредняя температура {temperature}°C.\n\nМаксимальная скорость ветра {max_wind_speed} км/ч.'
            await update.message.reply_text(message)

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Произошла ошибка при запросе прогноза: {e}")

# Функция для обработки текстовых сообщений
async def echo(update: Update, context: CallbackContext) -> None:
    # Проверяем тему
    thread_id = update.message.message_thread_id
    if thread_id in ALLOWED_TOPICS:
        await update.message.reply_text(update.message.text)
    else:
        logger.info(f"Сообщение из неразрешённой темы: {thread_id}")

# Функция main, которая будет запускать бота
def main():
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather_today", weather_today))
    application.add_handler(CommandHandler("weather_tomorrow", weather_tomorrow))

    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота
    #application.run_polling()
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=TOKEN,
        webhook_url=f"https://{os.getenv('HEROKU_APP_NAME')}.herokuapp.com/{TOKEN}"
    )

if __name__ == '__main__':
    main()