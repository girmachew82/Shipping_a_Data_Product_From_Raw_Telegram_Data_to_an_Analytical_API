from telethon import TelegramClient

api_id = 23207899

api_hash = '83370c840ded4ccde39f010638c92110'

# The first parameter is the .session file name (absolute paths allowed)
with TelegramClient('anon', api_id, api_hash) as client:
    client.loop.run_until_complete(client.send_message('me', 'Hello, myself!'))