import aiogram.types
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from tools import *
from base_tools import *

from PIL import Image

import io
import os

import logging
from config import TOKEN

logging.basicConfig(level=logging.INFO)


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


def done_(message):
    path = str(get_last_image(message.chat.id)[0])
    os.remove(path)
    update_is_on_server(message.chat.id, path)


@dp.message_handler(commands=['start'])
async def send_intro(message):
    reply = "Hello, this is your first step in using this bot. Submit " \
            "/help now to get the manual"
    await bot.send_message(message.chat.id, reply)


@dp.message_handler(commands=['help'])
async def send_manual(message):
    reply = "Manual \U0001F994\n"
    reply += "\U000027A1 /search \n"
    reply += " -   Search for an image on the Internet by request\n"
    reply += "\U000027A1 /resize. " \
             "\n -   Resizing by scaling with a given factor of 0.1z to 10z" \
             "\n -   Resizing in pixels from 50px to 1000px by setting the desired length of the maximum side\n"
    reply += "\U000027A1 /convert. \n" \
             " -   Convert image for any format from list: [png, jpg, jpeg, tiff, bmp, gif, jpeg 2000] \n"
    await bot.send_message(message.chat.id, reply)


@dp.callback_query_handler(lambda call: True)
async def callback_process(call: types.CallbackQuery):
    try:
        formats = ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif', 'jpeg 2000']
        for f in formats:
            if call.data == f:
                image_path = get_last_image(call.message.chat.id)[0]
                image_out, path_of_converted_image = convert_image(image_path, f)
                await bot.send_document(call.message.chat.id, document=image_out)

        # set command done
        update_is_done(call.message.chat.id, "convert")

        # delete converted image from server
        os.remove(path_of_converted_image)

        # delete user's image from server
        done_(call.message)
    except Exception as e:
        print(str(e))
        await bot.send_message(call.message.chat.id, "Processing of the previous photo is completed, " \
                                                     "please write /convert and send the photo to convert it again :)")



@dp.message_handler(commands=['search', 'resize', 'convert'])
async def search(message):
    """Find random pic in Google for resizing"""
    replies_list = ["Okay, enter what you want to find :)",
                    "Okay, send me an image :)",
                    "Okay, send me an image :)"]
    commands_list = ["search", "resize", "convert"]
    for i,j in zip(replies_list, commands_list):
        if message.text.split(' ')[0][1:] == j:
            insert_command([message.chat.id, j, False])
            await bot.send_message(message.chat.id, i)


@dp.message_handler(content_types='text')
async def message_text_processing(message):
    command_name = get_last_command(message.chat.id)[0]

    if command_name == "search":
        if await search_command(message):
            # set command done
            update_is_done(message.chat.id, command_name)
    elif command_name == "resize":
        if await resize_command(message):
            # set command done
            update_is_done(message.chat.id, command_name)
            # delete image from server
            done_(message)
        else:
            await bot.send_message(message.chat.id, "Please, send image :) /help")
    else:
        await bot.send_message(message.chat.id, "Request not recognized, check manual /help")


# photo handler for commands resize and convert
@dp.message_handler(content_types=['photo'])
async def photo_processing(message):

    command_name = get_last_command(message.chat.id)[0]

    if command_name in ["resize", "convert"]:
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)

        # load image in bytes
        file_path = file.file_path
        downloaded_file: io.BytesIO = (await bot.download_file(file_path))
        img = Image.open(downloaded_file)
        path_of_image_on_server = f"./{file_path[:-4]}_{str(message.chat.id)}.{str(img.format)}"
        img.save(path_of_image_on_server)
        insert([path_of_image_on_server, message.chat.id])

    if command_name == "resize":
        reply_message_resize = "Now send the photo change ratio (in coefficient z) " \
                               "or the new maximum size (in px) of one of the sides"
        await bot.send_message(message.chat.id, reply_message_resize)

    elif command_name == "convert":
        await convert_command(message)

    else:
        await bot.send_message(message.chat.id,
                               "Please select a command for image processing first, and then send a picture")


async def search_command(message):
    request = message.text

    if request:
        url_of_image = get_url(request)
        chat_id = message.chat.id
        if url_of_image != "":
            await bot.send_photo(chat_id, photo=url_of_image)
            return True
        else:
            await bot.send_message(chat_id,
                                   "Oops, no images found for this query, write the request more precisely")
            return False
    else:
        await bot.send_message(message, "Please, enter some query")
        return False


async def resize_command(message):
    request = message.text
    # load image path
    file_path = get_last_image(message.chat.id)

    if file_path:

        resize_exit_code, im_out = resize_image(file_path[0], request)
        if not resize_exit_code:
            await bot.send_message(message.chat.id, im_out)
        else:
            width, height = im_out.size
            caption_ = "New image size: %spx x %spx" % (str(width), str(height))

            bio = io.BytesIO()
            bio.name = 'image.jpeg'
            im_out.save(bio, im_out.format)
            bio.seek(0)
            await bot.send_photo(message.chat.id, photo=bio, caption=caption_)
            return True
    return False


async def convert_command(message):
    keyboard = ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif', 'jpeg 2000']

    # Create initial message:
    inline_markup = aiogram.types.InlineKeyboardMarkup()
    keyboard_list = []
    for k in keyboard:
        keyboard_list.append(aiogram.types.InlineKeyboardButton(text=k, callback_data=k))
    inline_markup.add(keyboard_list[0],
                      keyboard_list[1],
                      keyboard_list[2],
                      keyboard_list[3],
                      keyboard_list[4],
                      keyboard_list[5],
                      keyboard_list[6])

    await bot.send_message(message.chat.id, "Now send a new photo format", reply_markup=inline_markup)


def get_url(request):
    url = get_random(request)
    return url


if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)

