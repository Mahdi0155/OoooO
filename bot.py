from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackContext, JobQueue
import logging
from datetime import datetime, timedelta

# اطلاعات ربات
TOKEN = '7413532622:AAEZctC6bHJvAR5L8wWyDkySTszjlDvQP3o'
CHANNEL_USERNAME = '@hottof'
ADMINS = [7189616405, 5459406429, 6387942633]

# تنظیم لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# مراحل گفتگو
WAITING_FOR_MEDIA, WAITING_FOR_CAPTION, WAITING_FOR_ACTION, WAITING_FOR_SCHEDULE = range(4)

# دیتا موقت
user_data = {}

# شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text('شما دسترسی به این ربات ندارید.')
        return ConversationHandler.END
    await update.message.reply_text('سلام! لطفاً یک عکس یا ویدیو فوروارد کن.')
    return WAITING_FOR_MEDIA

# دریافت فایل
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return ConversationHandler.END

    file_id = None
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        media_type = 'photo'
    elif update.message.video:
        file_id = update.message.video.file_id
        media_type = 'video'
    else:
        await update.message.reply_text('فقط عکس یا ویدیو قابل قبول است. لطفاً دوباره ارسال کنید.')
        return WAITING_FOR_MEDIA

    user_data[update.effective_user.id] = {
        'file_id': file_id,
        'media_type': media_type,
    }

    await update.message.reply_text('لطفاً کپشن مورد نظر خود را بنویسید:')
    return WAITING_FOR_CAPTION

# دریافت کپشن
async def handle_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = update.message.text
    if update.effective_user.id not in user_data:
        await update.message.reply_text('مشکلی پیش آمده، لطفاً از اول شروع کنید.')
        return ConversationHandler.END

    final_caption = caption + "\n\n@hottof | تُفِ داغ"
    user_data[update.effective_user.id]['caption'] = final_caption

    # پیش نمایش فایل
    keyboard = ReplyKeyboardMarkup(
        [['ارسال در کانال', 'ارسال در آینده'], ['برگشت به ابتدا']],
        resize_keyboard=True
    )

    media_type = user_data[update.effective_user.id]['media_type']
    file_id = user_data[update.effective_user.id]['file_id']

    if media_type == 'photo':
        await update.message.reply_photo(file_id, caption=final_caption, reply_markup=keyboard)
    elif media_type == 'video':
        await update.message.reply_video(file_id, caption=final_caption, reply_markup=keyboard)

    return WAITING_FOR_ACTION

# پردازش انتخاب
async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == 'ارسال در کانال':
        await send_to_channel(context, user_id)
        await update.message.reply_text('پیام با موفقیت در کانال ارسال شد.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    elif text == 'ارسال در آینده':
        await update.message.reply_text('لطفاً زمان ارسال را به صورت دقیقه وارد کنید (مثلاً 5 یعنی 5 دقیقه بعد):', reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_SCHEDULE

    elif text == 'برگشت به ابتدا':
        await update.message.reply_text('لغو شد. دوباره یک فایل بفرستید.', reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_MEDIA

    else:
        await update.message.reply_text('لطفاً یکی از گزینه‌ها را انتخاب کنید.')
        return WAITING_FOR_ACTION

# زمان‌بندی ارسال
async def handle_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        minutes = int(update.message.text)
        send_time = datetime.utcnow() + timedelta(minutes=minutes)

        context.job_queue.run_once(send_scheduled, when=timedelta(minutes=minutes), data=user_id)

        await update.message.reply_text(f'پیام برای {minutes} دقیقه بعد زمان‌بندی شد.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text('لطفاً فقط عدد وارد کنید.')
        return WAITING_FOR_SCHEDULE

# ارسال مستقیم
async def send_to_channel(context: ContextTypes.DEFAULT_TYPE, user_id):
    if user_id not in user_data:
        return

    data = user_data[user_id]
    media_type = data['media_type']
    file_id = data['file_id']
    caption = data['caption']

    if media_type == 'photo':
        await context.bot.send_photo(chat_id=CHANNEL_USERNAME, photo=file_id, caption=caption)
    elif media_type == 'video':
        await context.bot.send_video(chat_id=CHANNEL_USERNAME, video=file_id, caption=caption)

# ارسال زمان‌بندی شده
async def send_scheduled(context: CallbackContext):
    user_id = context.job.data
    await send_to_channel(context, user_id)

# لغو
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('عملیات لغو شد.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# اجرای ربات
def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_MEDIA: [MessageHandler(filters.PHOTO | filters.VIDEO, handle_media)],
            WAITING_FOR_CAPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_caption)],
            WAITING_FOR_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_action)],
            WAITING_FOR_SCHEDULE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_schedule)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
