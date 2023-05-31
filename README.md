<p align="center">
    <img src="images/Sprite-0003.png" alt="ai-chatbot-logo"/>
</p>

<h1 align="center">AI-Chatbot</h1>

<p align="center">
    <a href="README.ru.md">Этот файл на русском языке [ 🇷🇺 ]</a>
</p>

<p align="center">
    <a href="https://github.com/immacool/ai-chatbot/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/immacool/ai-chatbot" alt="GitHub License"></a>
    <img src="https://img.shields.io/badge/python-v3.10%20%7C%20v3.11-blue" alt="Python version">
</p>

## 🚀 Introduction

AI-Chatbot is a conversational agent powered by OpenAI's GPT-3 model.
It's capable of generating human-like text responses,
making it useful for a wide range of applications from drafting emails, writing code,
creating written content, answering questions, tutoring, language translation,
and even simulating characters for video games.

## 🛠️ Installation

You can install and run the AI-Chatbot using either pip or Docker.

### Pip Installation

```bash
# Clone the repository
git clone https://github.com/fresh-milkshake/ai-chatbot.git

# Navigate into the repository
cd ai-chatbot

# Install dependencies
pip install -r requirements.txt
```

### Docker Installation

```bash
# Clone the repository
git clone https://github.com/fresh-milkshake/ai-chatbot.git

# Navigate into the repository
cd ai-chatbot

# Build the Docker image
docker build -t ai-chatbot:latest .

# Run the Docker container
docker run -p 8080:8080 ai-chatbot:latest
```

## 🎮 Usage

To run the bot:

```bash
python main.py
```

Or, if using Docker:

```bash
docker run -p 8080:8080 ai-chatbot:latest
```

## 🌐 API Keys

In order to interact with the OpenAI API,
you need to acquire an API key from OpenAI and set it as an environment variable.
    
```bash
export OPENAI_TOKEN=<your-api-key>
```

Also, you need to set the Telegram bot token as an environment variable.

```bash
export TELEGRAM_TOKEN=<your-bot-token>
```

Also, you can create a `.env` file in the root directory of the project.

Alternatively, you can pass the API key as an argument to the `main.py` script.

```bash
python main.py --openai-token <your-api-key> --telegram-token <your-bot-token>
```

## 📘 Dependencies

This project uses the following dependencies:

- python-telegram-bot - Telegram Bot API client
- python-dotenv - `.env` file reader
- openai - OpenAI API client
- redis - Redis client
- hiredis - Redis protocol reader
- loguru - logging and exception handling

## 🙌 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create.
Any contributions you make to the AI-Chatbot project are **greatly appreciated**.

- Fork the Project
- Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
- Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
- Push to the Branch (`git push origin feature/AmazingFeature`)
- Open a Pull Request

For major changes, please open an issue first to discuss what you would like to change. 

## 📝 License

This project is licensed under the terms of the [MIT](https://github.com/immacool/ai-chatbot/blob/master/LICENSE) license.