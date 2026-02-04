from keep_alive import keep_alive
keep_alive()
import telebot
import google.generativeai as genai

# --- CONFIGURATION (Paste your real keys here) ---
import os
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_KEY)

# Define the "Persona" of the bot
SYSTEM_INSTRUCTION = """
You are an expert Entrepreneurial Coach and Startup Mentor (like a mix of Paul Graham and Naval Ravikant).
Your goal is to help the user build successful businesses.
Guidelines:
1. Be concise and actionable. No fluff.
2. If the user asks a generic question, give a specific, strategic answer.
3. If the user greets you (Hi, Hello), welcome them and ask what they are building today.
4. Strictly answer only entrepreneurship, business, and mindset questions.
"""

print("👨‍💻 Startup Mentor Bot is running... (Press Ctrl+C to stop)")

def ask_gemini(user_question):
    """Sends the user's question to Gemini with the persona instructions"""
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    
    # Combine instructions with the user's specific question
    full_prompt = f"{SYSTEM_INSTRUCTION}\n\nUSER QUESTION: {user_question}"
    
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        return "⚠️ Brain freeze. I couldn't reach the servers. Try again?"

# --- THE LISTENER ---
# This handler catches ALL text messages (func=lambda msg: True)
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text
    print(f"📩 Received: {user_text} | From: {message.chat.first_name}")
    
    # 1. Send "Typing..." status (so it feels real)
    bot.send_chat_action(message.chat.id, 'typing')
    
    # 2. Get Answer
    ai_reply = ask_gemini(user_text)
    
    # 3. Reply
    # Telegram has a limit of 4096 chars per message. 
    # Gemini is usually concise, but if it's long, this handles it safely.
    if len(ai_reply) > 4000:
        for x in range(0, len(ai_reply), 4000):
            bot.reply_to(message, ai_reply[x:x+4000])
    else:
        bot.reply_to(message, ai_reply, parse_mode="Markdown")

# --- KEEP RUNNING ---
bot.infinity_polling()