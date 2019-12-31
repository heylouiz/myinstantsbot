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

### Run with Docker (Recommended)

To run this bot using Docker

```
docker build -t myinstantsbot .

docker run -t --name myinstantsbot \
              -e TELEGRAM_TOKEN='' \
              -e MYINSTANTS_USERNAME='' \
              -e MYINSTANTS_PASSWORD='' \
              myinstantsbot
```

Notes:
TELEGRAM_TOKEN='' needs to be replace with your bot token.
MYINSTANTS_USERNAME='' needs to be replaced with a myinstants.com username, in order to upload files
MYINSTANTS_PASSWORD='' needs to be replaced with a myinstants.com password, in order to upload files

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
TELEGRAM_TOKEN=<YOUR BOT'S TOKEN> MYINSTANTS_USERNAME=<MYINSTANTS USERNAME> MYINSTANTS_PASSWORD=<MYINSTANTS PASSWORD> python3 myinstantsbot.py
```


If you have any doubts let me know!
