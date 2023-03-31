# - *- coding: utf- 8 - *-
import configparser

# Токен бота
config = configparser.ConfigParser()
config.read("settings.ini")
BOT_TOKEN = config['settings']['token'].strip().replace(' ', '')
BOT_TIMEZONE = "Europe/Moscow"  # Временная зона бота


PATH_DATABASE = "tgbot/data/database.db"  # Путь к БД
PATH_LOGS = "tgbot/data/logs.log"  # Путь к Логам
BOT_VERSION = "3.4"  # Версия бота

crystal_name = config["crystal"]["nickname"]
crystal_secret = config["crystal"]["secret_1"]
payments_enabled = config["payments"]["enabled"]
redirect_url = config["payments"]["redirect_url"]
payments_enabled = payments_enabled.replace(" ", "").split(",")


# Получение администраторов бота
def get_admins() -> list[int]:
    read_admins = configparser.ConfigParser()
    read_admins.read("settings.ini")

    admins = read_admins['settings']['admin_id'].strip().replace(" ", "")

    if "," in admins:
        admins = admins.split(",")
    else:
        if len(admins) >= 1:
            admins = [admins]
        else:
            admins = []

    while "" in admins: admins.remove("")
    while " " in admins: admins.remove(" ")
    while "\r" in admins: admins.remove("\r")
    while "\n" in admins: admins.remove("\n")

    admins = list(map(int, admins))

    return admins


# УДАЛИШЬ ИЛИ ИЗМЕНИШЬ ССЫЛКИ НА ДОНАТ, КАНАЛ И ТЕМУ БОТА - КАСТРИРУЮ БЛЯТЬ <3
BOT_DESCRIPTION = f"""
<b>⚜ Bot Version: <code>{BOT_VERSION}</code>
🔗 Topic Link: <a href='https://lolz.guru/threads/1888814'>Click me</a>
♻ Bot created by @djimbox
🦍 Fork by @muertome
🍩 Donate to the author: <a href='https://qiwi.com/n/DJIMBO'>Click me</a>
🤖 Bot channel [NEWS | UPDATES]: <a href='https://t.me/DJIMBO_SHOP'>Click me</a></b>
""".strip()
