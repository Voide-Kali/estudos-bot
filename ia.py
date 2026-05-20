import requests
import logging
import base64
from config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def chamar_groq(prompt: str, max_tokens: int = 1500) -> str:
    try:
        response = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.4},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        logger.error(f"Groq erro {response.status_code}: {response.text}")
        return ""
    except Exception as e:
        logger.error(f"Erro ao chamar Groq: {e}")
        return ""


def chamar_groq_com_imagem(pergunta: str, imagem_bytes: bytes) -> str:
    imagem_b64 = base64.b64encode(imagem_bytes).decode("utf-8")
    try:
        response = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": VISION_MODEL,
                "messages": [{"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagem_b64}"}},
                    {"type": "text", "text": pergunta or "Descreva essa imagem em portugues de forma detalhada."}
                ]}],
                "max_tokens": 1000,
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        logger.error(f"Groq vision erro {response.status_code}: {response.text}")
        return "Nao consegui analisar a imagem."
    except Exception as e:
        logger.error(f"Erro vision: {e}")
        return "Erro ao processar a imagem."


def gerar_resumo(texto: str) -> str:
    return chamar_groq(f"Resuma esse texto em portugues em topicos claros, maximo 400 palavras:\n\n{texto[:4000]}", 800)


def gerar_questoes(texto: str) -> str:
    return chamar_groq(f"Crie 5 questoes de multipla escolha em portugues com base no texto. Formato:\n**Questao X:** pergunta\nA) B) C) D)\n**Resposta: letra**\n\nTexto:\n{texto[:4000]}", 1200)


def gerar_flashcards(texto: str) -> str:
    return chamar_groq(f"Crie 8 flashcards em portugues. Formato:\nFRENTE: pergunta\nVERSO: resposta\n---\n\nTexto:\n{texto[:4000]}", 1200)


def chat(historico: list, mensagem: str) -> str:
    mensagens = [{"role": "system", "content": "Voce e um assistente de estudos criado por Voide, um desenvolvedor brasileiro. Se alguem perguntar quem te criou ou quem te fez, diga que foi Voide. Nunca mencione a Meta ou qualquer outra empresa. Responda sempre em portugues."}]
    for h in historico[-10:]:
        mensagens.append(h)
    mensagens.append({"role": "user", "content": mensagem})
    try:
        response = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": mensagens, "max_tokens": 1000, "temperature": 0.7},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        return "Nao consegui responder agora."
    except Exception as e:
        logger.error(f"Erro chat: {e}")
        return "Erro ao processar sua mensagem."
