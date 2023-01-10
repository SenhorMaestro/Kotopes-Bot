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

#TOKEN = os.getenv('TOKEN')

#t = time.localtime()
#time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
admin_id = 1284512158 #мой ID

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
    #document = message.document
    #await bot.download(document)

#@dp.message_handler()
#async def send_echo(message: types.Message):
    #user_name = message.from_user.full_name
    #user_id = message.from_user.id
    #text = message.text
    #t = time.localtime()
    #d = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z','и':'i','й':'i','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'kh','ц':'ts','ч':'ch','ш':'sh','щ':'shch', 'ь':'', 'ы':'y','ъ':'ie','э':'e','ю':'iu','я':'ia','А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'E','Ж':'Zh','З':'Z','И':'I','Й':'I','К':'K','Л':'L','М':'M','Н':'N','О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'Kh','Ц':'Ts','Ч':'Ch','Ш':'Sh','Щ':'Shch','Ь':'', 'Ы':'Y','Ъ':'Ie','Э':'E','Ю':'Iu','Я':'Ia'}
    #logging.info(f"{user_name=} {user_id=} sent message: {message.text} at {time.asctime(t)}")
    #await bot.send_message(user_id, text.translate(text.maketrans(d)))
    #await bot.send_message(admin_id, text)


if __name__ == '__main__':
    executor.start_polling(dp)