# Vk copy post to telegram channel

## Technical requirement
1. Create telegram bot that will copy post from given VK user to the telegram channel after user will create new post.
2. The admin users can set pair of vk_user_id and telegram_channel_id.
    1. User send vk_user_id. Validate it using VK API.
    2. User send telegram_channel_id. Validate it using Telegram API. 
    3. After all validation, save to User table Vk account info and to Post table Last Post info. 
3. Celery periodic task.
    1. Every N-minutes start task to check new post for user.
    2. If new post is ready send it to the telegram_channel and admin users.

## Tools
- aiogram - Asynchronious framework to create telegram bots
- aiohttp - For creating Non-Blocking http client
- aioredis - Asynchronious redis client
- celery - Distributed Task Queue for periodic tasks
- pydantic - For settings management
- sentry - logging system
- watchfiles - for reloading in development process
- linters and formatters(mypy, flake8, isort, black, autoflake)

## Run application
1. Using docker-compose
     ```shell
    docker-compose up -d bot scheduler
    ```

2. Using shell
    1. Install requirements.txt
        ```shell
        poetry install
        ```
    2. Run start script
        ```shell
        ./docker/start.sh
        ```

## Deyloy application
1. Create .env file
2. Start using docker-compose
    ```shell
    docker-compose up -d bot scheduler
    ```

## Heroku setup
1. Login using heroku.
    ```shell
    heroku login
    ```
2. Add new remote repository
    ```shell
    heroku git:clone -a vk-copy-post-bot
    ```
3. Create new branch with Procfile, requirements.txt and runtime.txt.
4. Push change using custom branch
    ```shell
    git push heroku deploy/heroku:master
    ```

## Architecture 
Application consists of three layers: handlers, services, database.
- Handlers layer. Responsible for creating API route function, validation input user data.
- Service layer. It's a place for all business logic and additional validation.
- Database layer. Responsible for creating actual database queries and executing them.

## WIP
1. Add sphinx documendation.
2. Check using clean code.

