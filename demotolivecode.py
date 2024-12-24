import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

API_KEY = '7219812972:AAGwGsA7SwZEdMTdSvz2A_NBEAt8fKJi25Q'
CHANNEL_USERNAMES = ['@treaderjisanx', '@DvxORG']

bot = telebot.TeleBot(API_KEY)

# রেফারাল ডেটা সংরক্ষণ
user_referrals = {}
user_join_status = {}

# Keep-Alive সার্ভার
app = Flask('')


@app.route('/')
def home():
    return "Bot is running!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


# স্টার্ট কমান্ড
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    # রেফারেল চেক
    referrer_id = None
    if len(message.text.split()) > 1:
        referrer_id = message.text.split()[1]
        if referrer_id.isdigit() and int(referrer_id) != user_id:
            referrer_id = int(referrer_id)
            if referrer_id not in user_join_status:
                user_join_status[referrer_id] = set()
            user_join_status[referrer_id].add(user_id)

    if user_id not in user_referrals:
        user_referrals[
            user_id] = 0  # নতুন ইউজারের জন্য রেফারেল সংখ্যা শুরুতে 0
    send_start_message(message)


# স্টার্ট মেসেজ


def send_start_message(message):
    markup = InlineKeyboardMarkup()
    join_buttons = [
        InlineKeyboardButton(f"🔗 Join {channel}",
                             url=f"https://t.me/{channel[1:]}")
        for channel in CHANNEL_USERNAMES
    ]
    check_button = InlineKeyboardButton("✅ Check", callback_data="check_join")

    for button in join_buttons:
        markup.add(button)
    markup.add(check_button)

    bot.send_message(
        message.chat.id, "**English:**\n"
        "👉 **Demo To Live Code - Join our channels to get the code for free.** 🎉\n\n"
        "**Bangla:**\n"
        "👉 **Demo To Live Code ফ্রিতে পেতে চাইলে আমাদের টেলিগ্রাম চ্যানেলগুলোতে জয়েন করুন।** 🎉",
        parse_mode="Markdown",
        reply_markup=markup)


# চেক বাটন হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    user_id = call.from_user.id
    try:
        for channel in CHANNEL_USERNAMES:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                send_not_joined_message(call.message)
                return

        update_referral_count(user_id)
        send_work_instructions(call.message)
    except Exception as e:
        send_not_joined_message(call.message)


# কাজের নির্দেশিকা
def send_work_instructions(message):
    markup = InlineKeyboardMarkup()
    work_button = InlineKeyboardButton("📋 What Work?",
                                       callback_data="what_work")
    markup.add(work_button)

    bot.send_message(
        message.chat.id, "**English:**\n"
        "✅ **Thank you for joining our Telegram channels!** To get the free code, you need to complete some tasks. 💪\n\n"
        "**Bangla:**\n"
        "✅ **আপনাকে ধন্যবাদ আমাদের টেলিগ্রাম চ্যানেলগুলোতে জয়েন করার জন্য।** ফ্রি কোড পেতে আপনাকে কিছু কাজ করতে হবে। 💪",
        parse_mode="Markdown",
        reply_markup=markup)


# রেফারাল আপডেট
def update_referral_count(user_id):
    for referrer_id, joined_users in user_join_status.items():
        if user_id in joined_users:
            user_referrals[referrer_id] += 1
            joined_users.remove(user_id)  # একবার কাউন্ট করার পর রিমুভ করুন


# What Work বাটন
@bot.callback_query_handler(func=lambda call: call.data == "what_work")
def what_work(call):
    user_id = call.from_user.id
    referral_link = f"https://t.me/{bot.get_me().username}?start={user_id}"  # রেফারেল লিংক তৈরি

    markup = InlineKeyboardMarkup()
    invite_button = InlineKeyboardButton("👥 Invite 5 Friends",
                                         callback_data="invite_friends")
    markup.add(invite_button)

    bot.send_message(
        call.message.chat.id, f"**English:**\n"
        f"🎁 **To get the free coding file, refer 5 friends.**\n"
        f"Your unique referral link: **{referral_link}**\n\n"
        f"**Bangla:**\n"
        f"🎁 **ফ্রি কোডিং ফাইল পেতে আপনাকে ৫ জন বন্ধুকে রেফার করতে হবে।**\n"
        f"আপনার ইউনিক রেফারেল লিংক: **{referral_link}**",
        parse_mode="Markdown",
        reply_markup=markup)


# ইনভাইট সিস্টেম
@bot.callback_query_handler(func=lambda call: call.data == "invite_friends")
def invite_friends(call):
    user_id = call.from_user.id
    referral_link = f"https://t.me/{bot.get_me().username}?start={user_id}"  # রেফারেল লিংক তৈরি

    markup = InlineKeyboardMarkup()
    forward_button = InlineKeyboardButton(
        "🔄 Forward", url=f"https://t.me/share/url?url={referral_link}")
    complete_button = InlineKeyboardButton("✅ Complete",
                                           callback_data="check_completion")
    markup.add(forward_button, complete_button)

    referrals = user_referrals.get(user_id, 0)
    bot.send_message(
        call.message.chat.id, f"**English:**\n"
        f"📢 **Demo To Live Code Quotex coding is completely free.**\n"
        f"Your total referrals: **{referrals}**\n\n"
        f"**Bangla:**\n"
        f"📢 **Demo To Live Code Quotex কোডিংটি একদম ফ্রিতে দেওয়া হচ্ছে।**\n"
        f"আপনার মোট রেফার: **{referrals}**",
        parse_mode="Markdown",
        reply_markup=markup)


# রেফারাল সংখ্যা যাচাই
@bot.callback_query_handler(func=lambda call: call.data == "check_completion")
def check_completion(call):
    user_id = call.from_user.id
    referrals = user_referrals.get(user_id, 0)
    if referrals >= 5:
        send_free_file(user_id)
    else:
        bot.send_message(
            call.message.chat.id, f"**English:**\n"
            f"❌ **Your friends haven't joined yet. Total referrals: {referrals}.** Invite more friends. 🙏\n\n"
            f"**Bangla:**\n"
            f"❌ **আপনার মোট রেফার: {referrals}।** আপনার বন্ধুদের রেফার করুন। 🙏",
            parse_mode="Markdown")


# ফাইল পাঠানো
def send_free_file(user_id):
    bot.send_message(
        user_id, "**English:**\n"
        "🎉 **Congratulations! You successfully referred 5 friends.** Here's your free coding file. 🥳\n\n"
        "**Bangla:**\n"
        "🎉 **অভিনন্দন! আপনি সফলভাবে ৫ জন বন্ধুকে রেফার করেছেন।** এখানে আপনার ফ্রি কোডিং ফাইল। 🥳",
        parse_mode="Markdown")
    bot.send_document(user_id, open("free_code_file.zip", "rb"))


# যদি ইউজার জয়েন না করে
def send_not_joined_message(message):
    send_start_message(message)


# Keep-Alive সার্ভার চালু করুন
keep_alive()

# বট চালু রাখা
bot.polling(none_stop=True)

