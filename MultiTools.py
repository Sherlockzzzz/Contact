import asyncio
from telethon.sync import TelegramClient, events
import openai
from datetime import datetime, timedelta, timezone
import telethon
from googletrans import Translator
from telethon.sync import TelegramClient, events
from random import choice
from telethon.tl.types import InputMessagesFilterEmpty
from telethon.tl.functions.messages import DeleteMessagesRequest
from telethon.tl.functions.messages import DeleteMessagesRequest
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl import types





tool = LanguageTool('ru-RU')
api_id = '25827089'
api_hash = 'ba14acc31ce5751a487001e1c6b5a9f3'
phone_number = '+79650748375'
openai.api_key = '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'

client = TelegramClient('session_name', api_id, api_hash)

urrent_time_str = ''
HEART = '🤍'
COLORED_HEARTS = ['💗', '💓', '💖', '💘', '❤️', '💞']
MAGIC_PHRASES = ['magic']
EDIT_DELAY = 0.01

PARADE_MAP = '''
00000000000
00111011100
01111111110
01111111110
00111111100
00011111000
00001110000
00000100000
'''

async def auto_responder(event):
    if event.is_private:
        triggers = ['привет', 'hello', 'здравствуй', 'hi', 'Добрый вечер', 'здравствуйте', 'ку']
        for trigger in triggers:
            if trigger.lower() in event.message.text.lower():
                await event.reply('Привет! Владелец аккаунта скоро тебе ответит! (График 11:00-23:00)')


async def chat_gpt(event):
    if "!gpt" in event.message.text:
        prompt = event.message.text.split("!gpt")[1].strip()
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=400
        )["choices"][0]["text"]
        await event.edit(response)
        await asyncio.sleep(2)  



async def clear_chat(event):
    chunks = 3
    async for message in event.client.iter_messages(event.chat_id, limit=1, from_user='me'):
        for chunk in chunks:
            await message.edit(chunk)
            await asyncio.sleep(1)

async def update_nick_with_time(event):
    global current_time_str
    while True:
        moscow_time = datetime.utcnow() + timedelta(hours=3)
        formatted_time = moscow_time.strftime("[%H:%M]")

        # Обновляем ник, добавляя актуальное время
        if formatted_time != current_time_str:
            me = await event.client.get_me()
            current_first_name = me.first_name
            updated_first_name = f"{current_first_name} {formatted_time}"
            await event.client(telethon.tl.functions.account.UpdateProfileRequest(first_name=updated_first_name))
            current_time_str = formatted_time
        
        await asyncio.sleep(60)

async def translate_command(event):
    if "!tr" in event.message.text:
        translator = Translator()
        text_to_translate = event.message.text.split("!tr")[1].strip()

        try:
            translation = translator.translate(text_to_translate, src='ru', dest='en')
            await event.edit(f"{translation.text}")
        except Exception as e:
            await event.edit(f"Произошла ошибка при переводе: {str(e)}")

def generate_parade_colored():
    output = ''
    for c in PARADE_MAP:
        if c == '0':
            output += HEART
        elif c == '1':
            output += choice(COLORED_HEARTS)
        else:
            output += c
    return output


async def process_love_words(event: events.NewMessage.Event):
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love you')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love you forever')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love you forever💗')


async def process_build_place(event: events.NewMessage.Event):
    output = ''
    for i in range(8):
        output += '\n'
        for j in range(11):
            output += HEART
            await client.edit_message(event.peer_id.user_id, event.message.id, output)
            await asyncio.sleep(EDIT_DELAY / 2)


async def process_colored_parade(event: events.NewMessage.Event):
    for i in range(50):
        text = generate_parade_colored()
        await client.edit_message(event.peer_id.user_id, event.message.id, text)

        await asyncio.sleep(EDIT_DELAY)


@client.on(events.NewMessage(outgoing=True, pattern='!h'))
async def handle_parade(event: events.NewMessage.Event):
    await process_build_place(event)
    await process_colored_parade(event)
    await process_love_words(event)

async def grammar_check(event):
    if "!gram" in event.message.text:
        text_to_check = event.message.text.split("!gram")[1].strip()

        
        matches = tool.check(text_to_check)

        
        if matches:
            corrected_text = text_to_check

            # Используем matches
            for match in matches:
                if match.replacements:
                    corrected_text = corrected_text.replace(match.context, match.replacements[0])

            
            await event.edit(f"{corrected_text}")
        else:
            
            await event.edit(f"{text_to_check}")

async def delete_chat(event):
    if "!del" in event.message.text:
        
        async for message in event.client.iter_messages(event.chat_id):
            try:
                
                await event.client(DeleteMessagesRequest(id=[message.id]))
            except Exception as e:
                print(f"Ошибка при удалении сообщения {message.id}: {e}")

async def delete_chat_self(event):
    if "!del" in event.message.text:
        
        async for message in event.client.iter_messages(event.chat_id):
            try:
                
                await event.client.delete_messages(event.input_chat, [message.id])
            except Exception as e:
                print(f"Ошибка при удалении сообщения {message.id} у себя: {e}")



if __name__ == '__main__':
    client = TelegramClient('session_name', api_id, api_hash)
    client.start(phone_number)

    client.add_event_handler(auto_responder, events.NewMessage)
    client.add_event_handler(chat_gpt, events.NewMessage(pattern=r'!gpt'))
    client.add_event_handler(clear_chat, events.NewMessage(pattern=r'!clear'))
    client.add_event_handler(update_nick_with_time, events.NewMessage(pattern=r'!time'))
    client.add_event_handler(translate_command, events.NewMessage(pattern=r'!tr'))
    client.add_event_handler(handle_parade, events.NewMessage(pattern=r'!h'))
    client.add_event_handler(grammar_check, events.NewMessage(pattern=r'!gram'))
    client.add_event_handler(delete_chat, events.NewMessage(pattern=r'!del'))
    client.add_event_handler(delete_chat_self, events.NewMessage(pattern=r'!delself'))
    client.run_until_disconnected()
