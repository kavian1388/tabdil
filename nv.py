import telebot
from telebot import types
from threading import Timer
import time

# تنظیمات ربات
TOKEN = '7577409818:AAGNyN9WY1rIaFF91HBBagv5oFWTYw88N8o'
bot = telebot.TeleBot(TOKEN)

CHECK_INTERVAL = 60  # فاصله زمانی انتشار تبلیغات (بر حسب ثانیه)
USER_DELAY = 900  # محدودیت ارسال تبلیغ هر کاربر (۱۵ دقیقه)
ads_queue = []
last_ad_time = 0
user_last_ad_time = {}

# مشخصات کانال‌ها
MEMBERSHIP_CHANNEL = '@zapaskanal129268'  # کانالی که کاربران باید عضو شوند
TARGET_CHANNEL = '@keshavarzane_iran'  # کانالی که تبلیغات در آن منتشر می‌شود

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    join_button = types.InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{MEMBERSHIP_CHANNEL[1:]}")
    markup.add(join_button)

    bot.send_message(
        message.chat.id,
        f"سلام! برای تبلیغ در کانال باید ابتدا عضو کانال زیر شوید:\n{MEMBERSHIP_CHANNEL}",
        reply_markup=markup
    )
    bot.send_message(message.chat.id, "پس از عضویت، روی /continue بزنید.")


@bot.message_handler(commands=['continue'])
def check_membership(message):
    user_id = message.from_user.id
    status = bot.get_chat_member(MEMBERSHIP_CHANNEL, user_id).status

    if status in ["member", "administrator", "creator"]:
        bot.send_message(message.chat.id, "عضویت تایید شد. برای گذاشتن تبلیغ به موارد زیر توجه کنید:\n"
                                          "تبلیغات باید در یک بنر باشند و نباید شماره تماس و نام خود را فراموش کنید.\n"
                                          "هر 15 دقیقه یک بار می‌توانید تبلیغ ارسال کنید.")
        bot.register_next_step_handler(message, receive_ad)
    else:
        bot.send_message(message.chat.id, f"شما هنوز عضو کانال {MEMBERSHIP_CHANNEL} نشده‌اید. لطفاً ابتدا عضو شوید.")


def receive_ad(message):
    user_id = message.chat.id
    current_time = time.time()

    # بررسی محدودیت زمانی ارسال تبلیغ
    if user_id in user_last_ad_time and current_time - user_last_ad_time[user_id] < USER_DELAY:
        remaining_time = int(USER_DELAY - (current_time - user_last_ad_time[user_id]))
        bot.send_message(message.chat.id, f"لطفاً {remaining_time} ثانیه دیگر صبر کنید تا بتوانید تبلیغ جدید ارسال کنید.")
        return

    ad_content = {"text": None, "photo": None, "video": None}

    # جمع‌آوری محتوای تبلیغاتی
    if message.photo:
        ad_content["photo"] = {"file_id": message.photo[-1].file_id, "caption": message.caption}
    elif message.video:
        ad_content["video"] = {"file_id": message.video.file_id, "caption": message.caption}
    elif message.text:
        ad_content["text"] = message.text

    if not any(ad_content.values()):
        bot.send_message(message.chat.id, "لطفاً محتوای مناسبی شامل متن، عکس یا ویدیو ارسال کنید.")
        return

    ads_queue.append((user_id, ad_content))
    user_last_ad_time[user_id] = current_time
    bot.send_message(message.chat.id, "تبلیغ شما در صف قرار گرفت و به زودی در کانال منتشر خواهد شد.")
    schedule_ads()


def schedule_ads():
    global last_ad_time

    current_time = time.time()
    if ads_queue and current_time - last_ad_time >= CHECK_INTERVAL:
        user_id, ad_content = ads_queue.pop(0)
        last_ad_time = current_time

        # انتشار تبلیغ
        if ad_content["photo"]:
            bot.send_photo(TARGET_CHANNEL, ad_content["photo"]["file_id"], caption=ad_content["photo"]["caption"])
        elif ad_content["video"]:
            bot.send_video(TARGET_CHANNEL, ad_content["video"]["file_id"], caption=ad_content["video"]["caption"])
        elif ad_content["text"]:
            bot.send_message(TARGET_CHANNEL, ad_content["text"])

        bot.send_message(user_id, "تبلیغ شما در کانال منتشر شد.")

        # ارسال دکمه تبلیغ بعدی
        markup = types.InlineKeyboardMarkup()
        next_ad_button = types.InlineKeyboardButton("تبلیغ بعدی", callback_data="next_ad")
        markup.add(next_ad_button)
        bot.send_message(user_id, "برای ارسال تبلیغ جدید روی دکمه زیر کلیک کنید.", reply_markup=markup)

        # برنامه‌ریزی تبلیغ بعدی
        Timer(CHECK_INTERVAL, schedule_ads).start()


@bot.callback_query_handler(func=lambda call: call.data == "next_ad")
def handle_next_ad_request(call):
    user_id = call.from_user.id
    bot.send_message(user_id, "لطفاً بنر تبلیغاتی خود را ارسال کنید.")
    bot.register_next_step_handler(call.message, receive_ad)


bot.infinity_polling()