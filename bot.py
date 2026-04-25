import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

QUESTIONS = [
    {
        "id": 1,
        "text": "ما هو المبدأ الذي تعمل به Stack؟",
        "options": ["FIFO", "LIFO", "Random", "Circular"],
        "correct": 1,
        "explanation": "LIFO = Last In First Out"
    },
    {
        "id": 2,
        "text": "أسوأ حالة بحث في BST غير متوازنة؟",
        "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
        "correct": 2,
        "explanation": "تصبح O(n)"
    }
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_q'] = 0
    context.user_data['score'] = 0
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q_num = context.user_data['current_q']
    q = QUESTIONS[q_num]
    keyboard = [[InlineKeyboardButton(opt, callback_data=str(i))] for i, opt in enumerate(q['options'])]
    text = f"📚 س {q_num+1}/{len(QUESTIONS)}\n\n{q['text']}"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    q_num = context.user_data['current_q']
    q = QUESTIONS[q_num]
    selected = int(query.data)
    if selected == q['correct']:
        context.user_data['score'] += 1
        msg = f"✅ صحيح!\n\n{q['explanation']}"
    else:
        msg = f"❌ خطأ!\nالصحيح: {q['options'][q['correct']]}\n\n{q['explanation']}"
    await query.edit_message_text(msg)
    context.user_data['current_q'] += 1
    if context.user_data['current_q'] >= len(QUESTIONS):
        s, t = context.user_data['score'], len(QUESTIONS)
        await query.message.reply_text(f"🏁 انتهى!\nنتيجتك: {s}/{t} ({s/t*100:.1f}%)")
    else:
        await asyncio.sleep(1.5)
        await send_question(update, context)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل /start لبدء الاختبار")

def main():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print("لا يوجد توكن")
        return
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(handle))
    print("✅ البوت يعمل...")
    app.run_polling()

if __name__ == '__main__':
    main()
