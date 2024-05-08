# @Myinstantsbot

A Telegram bot written in Python that sends voice messages from http://www.myinstants.com.

Check it out: www.telegram.me/myinstantsbot

You can use it in any chat, try to use it by typing the command bellow and wait for the sounds to appear:
```
@myinstantsbot rick roll
```

## Installing dependencies and running

Note: Before start you need to create a telegram bot and get a token, check the oficial documentation here:

https://core.telegram.org/bots

Since this bot uses inline queries to search for sounds, you also need to enable it on your bot, check the oficial documentation here:

https://core.telegram.org/bots/inline

### Run with Docker (Recommended)

To run this bot using Docker

```
docker build -t myinstantsbot .

docker run -t --name myinstantsbot \
              -e TELEGRAM_TOKEN='' \
              myinstantsbot
```

Notes:

TELEGRAM_TOKEN='' needs to be replace with your bot token.

#### Run without Docker

##### Install Dependencies (Only works in Python3)

Create a virtualenv (Optional):
```bash
mkdir ~/virtualenv
virtualenv -p python3 ~/virtualenv
source ~/virtualenv/bin/activate
```

Install the requirements (if you are in a virtualenv, "sudo" is not necessary):
```bash
sudo pip3 install -r requirements.txt
```

Running:

After all the requirements are installed you can run the bot using the command:
```bash
TELEGRAM_TOKEN=<YOUR BOT'S TOKEN> python3 myinstantsbot.py
```


If you have any questions let me know!
