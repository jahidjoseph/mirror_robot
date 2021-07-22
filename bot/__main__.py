import shutil, psutil
import signal
import pickle
from pyrogram import idle
from bot import app
from os import execl, kill, path, remove
from sys import executable
import time
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async
from bot import dispatcher, updater, botStartTime, AUTHORIZED_CHATS
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, anime, stickers, search, delete, speedtest, usage


@run_async
def stats(update, context):
    currentTime = get_readable_time((time.time() - botStartTime))
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b>Bot Uptime:</b> {currentTime}\n' \
            f'<b>Total disk space:</b> {total}\n' \
            f'<b>Used:</b> {used}  ' \
            f'<b>Free:</b> {free}\n\n' \
            f'📊Data Usage📊\n<b>Upload:</b> {sent}\n' \
            f'<b>Download:</b> {recv}\n\n' \
            f'<b>CPU:</b> {cpuUsage}% ' \
            f'<b>RAM:</b> {memory}% ' \
            f'<b>DISK:</b> {disk}%'
    sendMessage(stats, context.bot, update)


@run_async
def start(update, context):
    start_string = f'''
Hi Sir, I'm Fast Mirror Bot!
I Can Mirror All Your Links to Google Drive. I Only Works For @PremiumAppsAccountFree Group. Type /{BotCommands.HelpCommand} To Get List of Available Commands!
'''
    sendMessage(start_string, context.bot, update)

@run_async
def chat_list(update, context):
    chatlist =''
    chatlist += '\n'.join(str(id) for id in AUTHORIZED_CHATS)
    sendMessage(f'<b>Authorized List:</b>\n{chatlist}\n', context.bot, update)


@run_async
def restart(update, context):
    restart_message = sendMessage("Restarting, Please wait!", context.bot, update)
    LOGGER.info(f'Restarting the Bot...')
    # Save restart message object in order to reply to it after restarting
    fs_utils.clean_all()
    with open('restart.pickle', 'wb') as status:
        pickle.dump(restart_message, status)
    execl(executable, executable, "-m", "bot")


@run_async
def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


@run_async
def log(update, context):
    sendLogFile(context.bot, update)


@run_async
def bot_help(update, context):
    help_string = f'''
/{BotCommands.HelpCommand}: To Get This Help Message!

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Starts Mirroring The Link To Google Drive!

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Starts Mirroring & If Downloaded File Is Any Archive, Extracts It To Google Drive!

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Starts Mirroring & Upload The Archived (.tar) Version Of The Downloaded File!

/{BotCommands.WatchCommand} [youtube-dl supported link]: Starts Mirror Through YouTube-DL. Click /{BotCommands.WatchCommand} For More Info!

/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Starts Mirror Through YouTube-DL & Make Archived (.tar) Before Uploading!

/{BotCommands.CancelMirror}: Reply To The Message By Which The Download Was Initiated & That Download Will Be Cancelled!

/{BotCommands.CloneCommand}: Copy File / Folder To Google Drive!

/{BotCommands.StatusCommand}: Shows A Status Of All The Downloads!

/{BotCommands.ListCommand} [search term]: Searches The Search Term In The Google Drive, If Found Replies With The Link!

/{BotCommands.StatsCommand}: Show Stats Of The Machine The Bot Is Hosted On! (Only For Bot Owner)

/{BotCommands.AuthorizeCommand}: Authorize A Chat or A User To Use The Bot! (Only For Bot Owner)

/{BotCommands.AuthListCommand}: See Authorized Chat List! (Only For Bot Owner)

/{BotCommands.LogCommand}: Get A Log File Of The Bot. Handy For Getting Crash Reports! (Only For Bot Owner)

This Bot Is Developed By @itspriyo 👑
'''
    sendMessage(help_string, context.bot, update)


def main():
    fs_utils.start_cleanup()
    # Check if the bot is restarting
    if path.exists('restart.pickle'):
        with open('restart.pickle', 'rb') as status:
            restart_message = pickle.load(status)
        restart_message.edit_text("Restarted Successfully!")
        LOGGER.info('Restarted Successfully!')
        remove('restart.pickle')

    start_handler = CommandHandler(BotCommands.StartCommand, start,
                                   filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter)
    authlist_handler = CommandHandler(BotCommands.AuthListCommand, chat_list, filters=CustomFilters.owner_filter)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    dispatcher.add_handler(authlist_handler)
    updater.start_polling()
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
