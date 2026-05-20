import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.request import HTTPXRequest
import config
from pdf_utils import extrair_texto
from ia import gerar_resumo, gerar_questoes, gerar_flashcards, chat, chamar_groq_com_imagem

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

textos_usuarios = {}
historicos = {}
aguardando_pergunta_foto = {}
TEMP_DIR = "temp_pdfs"
os.makedirs(TEMP_DIR, exist_ok=True)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ola! Sou seu assistente de estudos.\n\n"
        "O que posso fazer:\n"
        "- Mande um PDF para gerar resumo, questoes e flashcards\n"
        "- Mande uma foto para eu analisar\n"
        "- Me mande qualquer mensagem para conversar\n\n"
        "Comandos:\n"
        "/limpar - limpar historico do chat"
    )


async def cmd_limpar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    historicos[chat_id] = []
    await update.message.reply_text("Historico limpo!")


async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    documento = update.message.document

    if not documento.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("Por favor, mande apenas arquivos PDF.")
        return

    await update.message.reply_text("Recebido! Baixando o PDF...")

    try:
        arquivo = await context.bot.get_file(documento.file_id, read_timeout=60, connect_timeout=60)
        caminho = os.path.join(TEMP_DIR, f"{chat_id}.pdf")
        await arquivo.download_to_drive(caminho, read_timeout=120, connect_timeout=60)
    except Exception as e:
        await update.message.reply_text(f"Erro ao baixar o PDF. Tente novamente.")
        return

    texto = extrair_texto(caminho)

    if not texto or len(texto) < 100:
        await update.message.reply_text("Nao consegui extrair texto desse PDF. Tente um PDF com texto selecionavel.")
        return

    textos_usuarios[chat_id] = texto
    palavras = len(texto.split())

    botoes = [
        [InlineKeyboardButton("Resumo", callback_data="resumo")],
        [InlineKeyboardButton("Questoes de multipla escolha", callback_data="questoes")],
        [InlineKeyboardButton("Flashcards", callback_data="flashcards")],
        [InlineKeyboardButton("Tudo de uma vez", callback_data="tudo")],
    ]
    await update.message.reply_text(
        f"PDF processado!\nTotal de palavras: {palavras}\n\nO que voce quer gerar?",
        reply_markup=InlineKeyboardMarkup(botoes)
    )


async def handle_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    legenda = update.message.caption or ""

    await update.message.reply_text("Analisando a imagem...")

    try:
        foto = update.message.photo[-1]
        arquivo = await context.bot.get_file(foto.file_id, read_timeout=60, connect_timeout=60)
        caminho = os.path.join(TEMP_DIR, f"{chat_id}_foto.jpg")
        await arquivo.download_to_drive(caminho, read_timeout=60, connect_timeout=60)

        with open(caminho, "rb") as f:
            imagem_bytes = f.read()

        resposta = chamar_groq_com_imagem(legenda, imagem_bytes)
        await update.message.reply_text(resposta)

    except Exception as e:
        logger.error(f"Erro ao processar foto: {e}")
        await update.message.reply_text("Erro ao analisar a imagem. Tente novamente.")


async def handle_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    texto = update.message.text

    if chat_id not in historicos:
        historicos[chat_id] = []

    await update.message.chat.send_action("typing")

    resposta = chat(historicos[chat_id], texto)

    historicos[chat_id].append({"role": "user", "content": texto})
    historicos[chat_id].append({"role": "assistant", "content": resposta})

    await update.message.reply_text(resposta)


async def handle_botao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = str(query.message.chat_id)
    acao = query.data

    if chat_id not in textos_usuarios:
        await query.edit_message_text("Nao encontrei seu PDF. Mande o arquivo novamente.")
        return

    texto = textos_usuarios[chat_id]
    await query.edit_message_text("Gerando conteudo com IA, aguarde...")

    if acao == "resumo":
        await query.message.reply_text(f"RESUMO\n\n{gerar_resumo(texto)}")
    elif acao == "questoes":
        await query.message.reply_text(f"QUESTOES\n\n{gerar_questoes(texto)}")
    elif acao == "flashcards":
        await query.message.reply_text(f"FLASHCARDS\n\n{gerar_flashcards(texto)}")
    elif acao == "tudo":
        await query.message.reply_text("Gerando tudo, aguarde...")
        await query.message.reply_text(f"RESUMO\n\n{gerar_resumo(texto)}")
        await query.message.reply_text(f"QUESTOES\n\n{gerar_questoes(texto)}")
        await query.message.reply_text(f"FLASHCARDS\n\n{gerar_flashcards(texto)}")

    botoes = [
        [InlineKeyboardButton("Resumo", callback_data="resumo")],
        [InlineKeyboardButton("Questoes", callback_data="questoes")],
        [InlineKeyboardButton("Flashcards", callback_data="flashcards")],
        [InlineKeyboardButton("Tudo de uma vez", callback_data="tudo")],
    ]
    await query.message.reply_text("Quer gerar mais alguma coisa?", reply_markup=InlineKeyboardMarkup(botoes))


def main():
    request = HTTPXRequest(connect_timeout=60, read_timeout=120)
    app = Application.builder().token(config.TELEGRAM_TOKEN).request(request).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("limpar", cmd_limpar))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(MessageHandler(filters.PHOTO, handle_foto))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mensagem))
    app.add_handler(CallbackQueryHandler(handle_botao))
    logger.info("Assistente de estudos iniciado!")
    app.run_polling()


if __name__ == "__main__":
    main()
