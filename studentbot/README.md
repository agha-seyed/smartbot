# StudentBot

This is a comprehensive Telegram bot for students, providing various services like scholarship search, ISEE calculation, weather updates, and more.

## Running the bot with Docker

### Prerequisites
- Docker
- Docker Compose

### 1. Create a `.env` file
Create a `.env` file in the root directory of the project by copying the example file:
```bash
cp .env.example .env
```
Now, open the `.env` file and fill in the required environment variables, such as your `TELEGRAM_TOKEN` and `ADMIN_CHAT_ID`.

### 2. Place your Google Credentials
Place your Google Cloud credentials JSON file in the root of the project and name it `credentials.json`. This file is necessary for the bot to interact with Google Sheets.

### 3. Build and Run the bot
You can use the provided scripts to build and run the bot:

**To build the Docker image:**
```bash
bash build.sh
```

**To run the bot in detached mode:**
```bash
bash run.sh
```

**To view the logs:**
```bash
docker-compose logs -f bot
```

**To stop the bot:**
```bash
docker-compose down
```
