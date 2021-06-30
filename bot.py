import telebot
from telebot import types
import instaloader
from instaloader import Post, Profile
import os
import shutil
from time import sleep

from telebot.types import KeyboardButton, InlineKeyboardMarkup
from helper import print_log

TOKEN = "TOKEN"
ig = instaloader.Instaloader()
ig.login("LOGIN", "PASSWORD")

print_log("Logged in! Ready to work!")


bot = telebot.TeleBot(TOKEN, parse_mode=None)

def gen_markup():
    markup = types.ReplyKeyboardMarkup()
    markup.row_width = 1
    markup.add(KeyboardButton("Post"),
    KeyboardButton("Stories"),
    KeyboardButton("Profile Picture"),
    KeyboardButton("Highlights")) #,
    # KeyboardButton("All data from account"))
    return markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    name = message.from_user.first_name
    bot.send_message(message.chat.id, "Hi, " + name + ". I can download photos and videos from Instagram!", reply_markup=gen_markup())

@bot.message_handler(func=lambda m:True)
def main_menu(message):
    if message.text == 'Post':
        msg = bot.reply_to(message, 'Send me the link to post')
        bot.register_next_step_handler(msg, download_post)
    elif message.text == 'Stories':
        msg = bot.reply_to(message, "Send me the username")
        bot.register_next_step_handler(msg, download_stories)
    elif message.text == 'Profile Picture':
        msg = bot.reply_to(message, "Send me the username")
        bot.register_next_step_handler(msg, download_profile_pic)
    elif message.text == 'Highlights':
        msg = bot.reply_to(message, "Send me the username")
        bot.register_next_step_handler(msg, download_highlights)

def download_post(message):
    url = message.text.split('/')
    print_log()
    print(url)
    if 'https:' not in url or 'www.instagram.com' not in url:
        bot.send_message(message.chat.id, "Sorry, this is not a link!")
        print_log("Received not a link")
        return
    print(url[len(url)-2])
    ident = url[len(url)-2]
    bot.send_message(message.chat.id, "In progress... Wait for message!")
    post = Post.from_shortcode(ig.context, ident)
    d = ig.download_post(post, ident)
    if d:
        for im in os.listdir(ident):
            if im.endswith(".jpg"):
                photo = open(ident+"/"+im, 'rb')
                bot.send_photo(message.chat.id, photo)
                print_log("Photo sent!")
            elif im.endswith(".mp4"):
                video = open(ident+'/'+im, 'rb')
                bot.send_video(message.chat.id, video)
                print_log("Video sent!")
            elif im.endswith(".txt"):
                text = open(ident+"/"+im, 'r')
                bot.send_message(message.chat.id, text)

        shutil.rmtree(ident, ignore_errors=True)
        print("Deleted files "+ident+"!")

def download_stories(message):
    username = message.text
    username = username.replace("@", "")
    print_log(username)
    profile = Profile.from_username(ig.context, username)
    list = [profile.userid]
    print_log(profile.userid)
    bot.send_message(message.chat.id, "Downloading stories... Wait for message!")
    ig.download_stories(list, False, username, None)
    if os.path.exists(username):
        print_log("Downloaded all stories!")
        for im in os.listdir(username):
            if im.endswith(".jpg"):
                photo = open(username+"/"+im, 'rb')
                bot.send_photo(message.chat.id, photo)
                print_log("Photo sent!")
            elif im.endswith(".mp4"):
                video = open(username+'/'+im, 'rb')
                bot.send_video(message.chat.id, video)
                print_log("Video sent!")
         
        shutil.rmtree(username, ignore_errors=True)
        print("Deleted files " + username + "!")
    else:
        bot.send_message(message.chat.id, "Stories to download doesen't exists! Try later...")

def download_profile_pic(message):
    username = message.text
    username = username.replace("@", "")
    print_log(username)
    profile = Profile.from_username(ig.context, username)
    print_log(username)
    bot.send_message(message.chat.id, "Downloading profile picture... Wait for message!")
    ig.download_profilepic(profile)
    if os.path.exists(username):
        print_log("Downloaded profile pic!")
        for im in os.listdir(username):
            if im.endswith(".jpg"):
                photo = open(username+"/"+im, 'rb')
                bot.send_photo(message.chat.id, photo)
                print_log("Photo sent!")

        shutil.rmtree(username, ignore_errors=True)

def download_highlights(message):
    username = message.text
    username = username.replace("@", "")
    print_log(username)
    profile = Profile.from_username(ig.context, username)
    it = ig.get_highlights(profile)
    st = ""
    y = 0
    for x in it:
        y += 1
        st += str(y) + ". "
        st += str(x)
        st += '\n'
    st = st.replace("<", "")
    st = st.replace(">", "")
    print_log(st)
    bot.send_message(message.chat.id, "Avaliable highlights: \n" + st)
    print_log("Downloading highlight "+username)
    bot.send_message(message.chat.id, "Downloading highlights... Wait for message!")
    d = ig.download_highlights(profile.userid, False, username, None)
    if os.path.exists(username):
        print_log("Downloaded highlights")
        for im in os.listdir(username):
            if im.endswith(".jpg"):
                photo = open(username+"/"+im, 'rb')
                bot.send_photo(message.chat.id, photo)
                print_log("Photo sent!")

        shutil.rmtree(username, ignore_errors=True)
    else:
        bot.send_message(message.chat.id, "Can't download highlights!")


bot.polling(none_stop=True)
