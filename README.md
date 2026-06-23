# Central de Estudos (Telegram)

Assistente de estudos com painel interativo, suporte a PDF, imagens, chat,
resumos, questões e flashcards. Usa Gemini ou Groq.

## Instalação (Kali/Linux)

```bash
git clone https://github.com/Voide-Kali/estudos-bot.git
cd estudos-bot
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cp config.example.py config.py
```

Edite o `.env`, preencha `TELEGRAM_TOKEN` e escolha pelo menos um provedor:

- `GEMINI_API_KEY` para Gemini;
- `GROQ_API_KEY` para Groq.

Use `AI_PROVIDER=auto` para preferir Gemini e usar Groq como alternativa.
Defina `ALLOWED_CHAT_IDS` para restringir o acesso.

## Rodar

```bash
cd estudos-bot
. .venv/bin/activate
python3 main.py
```

## Pegar seu chat_id (pra whitelist)

1) Inicie o bot e mande `/start` pra ele no Telegram.
2. Use o comando `/chatid`.
3. Coloque o valor retornado em `ALLOWED_CHAT_IDS`.
