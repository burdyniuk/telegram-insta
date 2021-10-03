import telebot
from telebot import types
import instaloader
from instaloader import Post, Profile
import os
import shutil
from time import sleep
import flask

from telebot.types import KeyboardButton, InlineKeyboardMarkup
from helper import print_log

TOKEN = "1712589824:AAGEamtzwPC4FJQnYH67I8vlFaBW7WFL2LA"
ig = instaloader.Instaloader()
ig.login("telegrambots_insta", "password0192")

print_log("Logged in! Ready to work!")

WEBHOOK_HOST = '80.249.144.141'
WEBHOOK_PORT = 8443
WEBHOOK_LISTEN = '80.249.144.141'

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (TOKEN)

bot = telebot.TeleBot(TOKEN, parse_mode=None)
app = flask.Flask(__name__)

#@app.route('/', methods=['GET', 'HEAD'])
#def index():
#    return ''

#@app.route(WEBHOOK_URL_PATH, methods=['POST'])
#def webhook():
#    if flask.request.headers.get('content-type') == 'application/json':
#        json_string = flask.request.get_data().decode('utf-8')
#        update = telebot.types.Update.de_json(json_string)
#        bot.process_new_updates([update])
#        return ''
#    else:
#        flask.abort(403)


def gen_markup():
    markup = types.ReplyKeyboardMarkup()
    markup.row_width = 1
    markup.add(KeyboardButton("Post"),
    KeyboardButton("Stories"),
    KeyboardButton("Profile Picture"),
    KeyboardButton("Highlights"),
    KeyboardButton("IGTV"),
    KeyboardButton("All data from account"))
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    name = message.from_user.first_name
    bot.send_message(message.chat.id, "Hi, " + name + ". I can download photos and videos from Instagram! Choose what type of media you want to download and follow the instructions.", reply_markup=gen_markup())

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
    elif message.text == 'All data from account':
        msg = bot.reply_to(message, "Send me the username")
        bot.register_next_step_handler(msg, download_account)
    elif message.text == 'IGTV':
        msg = bot.reply_to(message, "Send me the username")
        bot.register_next_step_handler(msg, download_igtv)
    else:
        bot.send_message(message.chat.id, "I don't understand you, sorry...")

def download_post(message):
    print_log("Request from: "+str(message.from_user.id))
    url = message.text.split('/')
    print_log(url)
    if 'https:' not in url or 'www.instagram.com' not in url:
        bot.send_message(message.chat.id, "Sorry, this is not a link to download!")
        print_log("Received not a link")
        return
    print(url[len(url)-2])
    ident = url[len(url)-2]
    bot.send_message(message.chat.id, "In progress... Wait for message!")
    try:
        post = Post.from_shortcode(ig.context, ident)
        d = ig.download_post(post, ident)
    except:
        print("Error")
        bot.send_message(message.chat.id, "Error! Can't download, verify if your message is correct or account is public.")
    
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
    username = username.lower()
    username = username.replace("@", "")

    print_log("Request from: "+str(message.from_user.id))
    print_log(username)
    
    try:
        profile = Profile.from_username(ig.context, username)
        list = [profile.userid]
        print_log(profile.userid)
        bot.send_message(message.chat.id, "Downloading stories... Wait for message!")
        ig.download_stories(list, False, username, None)
    except:
        print("Error")
        bot.send_message(message.chat.id, "Error! Can't download, verify if your message is correct or account is public.")
    
    if os.path.exists(username):
        print_log("Downloaded all stories!")
        for im in os.listdir(username):
            if im.endswith(".jpg"):
                name = im.split('.')
                nm = name[0]
                nm += ".mp4"
                if nm in os.listdir(username):
                    pass
                else:
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
    username = username.lower()
    username = username.replace("@", "")
    print_log("Request from: "+str(message.from_user.id))
    print_log(username)
    try:
        profile = Profile.from_username(ig.context, username)
        print_log(username)
        bot.send_message(message.chat.id, "Downloading profile picture... Wait for message!")
        ig.download_profilepic(profile)
    except:
        print_log("Error")
        bot.send_message(message.chat.id, "Error! Can't download, verify if your message is correct or account is public.")
    if os.path.exists(username):
        print_log("Downloaded profile pic!")
        for im in os.listdir(username):
            if im.endswith(".jpg"):
                photo = open(username+"/"+im, 'rb')
                bot.send_photo(message.chat.id, photo)
                print_log("Photo sent!")

        shutil.rmtree(username, ignore_errors=True)
        print("Deleted files "+username+"!")

    else:
        bot.send_message(message.chat.id, "Can't download profile picture!")

def download_highlights(message):
    username = message.text
    username = username.lower()
    username = username.replace("@", "")
    print_log("Request from: "+str(message.from_user.id))
    print_log(username)
    try:

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
    except:
        print_log("Error")
        bot.send_message(message.chat.id, "Error! Can't download, verify if your message is correct or account is public.")
    
    if os.path.exists(username):
        print_log("Downloaded highlights")
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
        print("Deleted files "+username+"!")

    else:
        bot.send_message(message.chat.id, "Can't download highlights!")

def download_igtv(message):
    username = message.text
    username = username.lower()
    username = username.replace("@", "")
    print_log("Request from: "+str(message.from_user.id))
    print_log("Download igtv: " + username)
    try:
        bot.send_message(message.chat.id, "Downloading IGTVs... Wait for message!")
        profile = Profile.from_username(ig.context, username)
        ig.download_igtv(profile, False, None)
    except:
        print_log("Error")
        bot.send_message(message.chat.id, "Error! Can't download, verify if your message is correct or account is public.")
    
    if os.path.exists(username):
        print_log("Downloaded igtv")
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
        print("Deleted files "+username+"!")

    else:
        bot.send_message(message.chat.id, "Can't download IGTV!")


def download_account(message):
    username = message.text
    username = username.lower()
    username = username.replace("@", "")
    print_log("Request from: "+str(message.from_user.id))
    try:
        print_log("Download profile: " + username)
        bot.send_message(message.chat.id ,"Downloading profile... Wait for message!")
        profile = Profile.from_username(ig.context, username)
        profiles = {profile}
        ig.download_profiles(profiles, True, True, False, True, True, True, False, None, None, False)
    except:
        print_log("Error")
        bot.send_message(message.chat.id, "Can't donwload, verify if your message is correct or account is public.")
    
    if os.path.exists(username):
        print_log("Profile downloaded")
        for fl in os.listdir(username):
            if os.path.isdir(username+'/'+fl):
                bot.send_message(message.chat.id, fl+":")
                for im in os.listdir(username+'/'+fl):
                    print_log("Sending "+fl)
                    if im.endswith(".jpg"):
                        if im.endswith("cover.jpg"):
                            bot.send_message(message.chat.id, "Cover of highlight:")
                        photo = open(username+"/"+fl+'/'+im, 'rb')
                        bot.send_photo(message.chat.id, photo)
                        print_log("Photo sent!")
                    elif im.endswith(".mp4"):
                        video = open(username+'/'+fl+'/'+im, 'rb')
                        bot.send_video(message.chat.id, video)
                        print_log("Video sent!")

        bot.send_message(message.chat.id, "Posts:")
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
        print("Deleted files "+username+"!")

    else:
        bot.send_message(message.chat.id, "Can't download profile!")

bot.remove_webhook()

#sleep(0.1)

#bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

#app.run(host=WEBHOOK_LISTEN,
#        port=WEBHOOK_PORT,
#        debug=True)

bot.polling(none_stop=True)
