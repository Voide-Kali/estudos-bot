# Central de Estudos

Bot do Telegram para estudo guiado com suporte a PDF, imagens, chat, resumos, questões e flashcards. Usa Gemini ou Groq.

## Componentes

- `main.py`: fluxo principal do bot
- `ia.py`: integração com modelos de IA
- `pdf_utils.py`: leitura e preparação de PDF
- `config.py` e `config.example.py`: configuração local
- `systemd/estudos-bot.service`: execução como serviço

## Instalação

```bash
git clone https://github.com/Voide-Kali/estudos-bot.git
cd estudos-bot
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cp config.example.py config.py
```

## Configuração

- preencha `TELEGRAM_TOKEN`;
- escolha pelo menos um provedor entre `GEMINI_API_KEY` e `GROQ_API_KEY`;
- use `AI_PROVIDER=auto` para preferir Gemini e cair para Groq se precisar;
- ajuste `ALLOWED_CHAT_IDS` para restringir o acesso.

## Execução

```bash
. .venv/bin/activate
python3 main.py
```

## Serviço systemd

```bash
sudo install -m 0644 systemd/estudos-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now estudos-bot.service
```

## Estrutura

```text
estudos-bot/
├── main.py
├── ia.py
├── pdf_utils.py
├── config.py
├── config.example.py
├── systemd/
└── README.md
```

## Governança

- [LICENSE](LICENSE)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CHANGELOG.md](CHANGELOG.md)
