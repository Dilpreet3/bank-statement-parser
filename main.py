import os
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import pdfplumber
import pandas as pd
from utils.parser import parse_bank_statement

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a bank statement PDF and I'll extract the data for you.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.document.get_file()
        file_path = f"temp_{update.message.document.file_name}"
        await file.download_to_drive(file_path)

        print("[INFO] Extracting text from PDF...")
        with pdfplumber.open(file_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"

        print("[INFO] Parsing transactions...")
        transactions = parse_bank_statement(full_text)

        if not transactions:
            await update.message.reply_text("❌ No transactions found in this file.")
            os.remove(file_path)
            return

        df = pd.DataFrame(transactions)
        csv_path = "output.csv"
        xlsx_path = "output.xlsx"
        df.to_csv(csv_path, index=False)
        df.to_excel(xlsx_path, index=False)

        await update.message.reply_text("✅ Here is your parsed transaction data:")
        await update.message.reply_document(document=open(csv_path, "rb"))
        await update.message.reply_document(document=open(xlsx_path, "rb"))

        os.remove(file_path)
        os.remove(csv_path)
        os.remove(xlsx_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        print(f"[FATAL ERROR] {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_file))

    print("Bot is running...")
    app.run_polling()
