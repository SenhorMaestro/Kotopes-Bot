import os
import logging
import time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms as T
from torchvision import io
from torchvision.models import resnet50, ResNet50_Weights
from random import randint

from aiogram import Bot, Dispatcher, executor, types

from config import TOKEN

logging.basicConfig(filename = 'logfile.log', level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
admin_id = ...

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_name = message.from_user.full_name
    user_id = message.from_user.id
    t = time.localtime()
    text = f'Привет, {user_name}. Я телеграм-бот, эксперт по собачкам и кошкам. Присылай картинку кота или собачки, выражу своё экспертное мнение. Не надо присылать мне другие картинки, моя экспертная область - котопсы и только!!!'
    logging.info(f"{user_name=} {user_id=} sent message: {message.text} at {time.asctime(t)}")
    await message.reply(text)

@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message):
    user_name = message.from_user.full_name
    user_id = message.from_user.id
    t = time.localtime()
    logging.info(f"{user_name=} {user_id=} sent message: {message.photo[-1]} at {time.asctime(t)}")

    await message.photo[-1].download('test.jpg')

    photo = open('test.jpg', 'rb')
    resize = T.Resize((224, 224))
    img = resize(io.read_image('test.jpg')/255)

    weights = ResNet50_Weights.DEFAULT
    loaded_model = resnet50(weights=weights)
    loaded_model.fc = nn.Linear(in_features=2048, out_features=1, bias=True)
    loaded_model.load_state_dict(torch.load('model_resnet50_weights.pt', map_location=torch.device('cpu')))
    label = str(int(torch.sigmoid(loaded_model(img.unsqueeze(0))).round().item()))
    dict_labels = {'0':'кошка', '1':'собака'}
    nabor_fraz = ['Ответственно заявляю, что на фото ', 'Не, ну тут ясно, что ', 'Экспертно заявляю: перед нами ', 'Я отвечаю, это ','Зуб даю, это ']
    await bot.send_message(user_id, nabor_fraz[randint(0,4)]+label.translate(label.maketrans(dict_labels)))
    await bot.send_message(admin_id, "Админ, лови: ")
    await bot.send_photo(admin_id, photo)
    await bot.send_message(admin_id, 'Я предсказал: '+label.translate(label.maketrans(dict_labels)))
  

if __name__ == '__main__':
    executor.start_polling(dp)
