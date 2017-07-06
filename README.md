**How to play?**

Read the [GUIDE](GUIDE.md).

**Install required packages**
```
sudo apt install python3.6 python3.6-dev libusb-1.0-0-dev libudev-dev

wget https://bootstrap.pypa.io/get-pip.py
sudo python3.6 get-pip.py
sudo pip install virtualenv
```

**Setup virtual environment and install requirements**
```
virtualenv venv -p python3.6
source venv/bin/activate
pip install -r requirements.txt
```

**ENVIRONMENT VARIABLES**

Name | Default value | Description
--------|---------------|-------------
OG_GAME_START_TIME_BUFFER | 10 | Amount of seconds before a player can win, this functions as a buffer, so that nobody wins by "accident"
OG_GAME_CARD_REGISTRATION_TIMEOUT | 3600 | Amount of seconds before a new card registration times out
OG_GAME_PLAYER_REGISTRATION_TIMEOUT | 30 | Amount of seconds before another player has to register their card to start a new game
OG_GAME_SESSION_TIME| 900 | Amount of seconds before a game session runs out (in the case when players forget to register a winner)
OG_FIREBASE_API_KEY | None | See Firebase for more information
OG_FIREBASE_DATABASE_URL| None | Database of the Firebase application
OG_FIREBASE_STORAGE_BUCKET| None | Storage bucket of the Firebase application (not used)
OG_FIREBASE_AUTH_DOMAIN | None | See Firebase for more information
OG_FIREBASE_TYPE| service_account | See Firebase for more information
OG_FIREBASE_PROJECT_ID| None | See Firebase for more information
OG_FIREBASE_PRIVATE_KEY_ID| None | See Firebase for more information
OG_FIREBASE_PRIVATE_KEY | None | See Firebase for more information
OG_FIREBASE_CLIENT_EMAIL| None | See Firebase for more information
OG_FIREBASE_CLIENT_ID | None | See Firebase for more information
OG_FIREBASE_AUTH_URI| https://accounts.google.com/o/oauth2/auth | See Firebase for more information
OG_FIREBASE_TOKEN_URI | https://accounts.google.com/o/oauth2/token | See Firebase for more information
OG_FIREBASE_AUTH_PROVIDER_X509_CERT_URL | https://www.googleapis.com/oauth2/v1/certs | See Firebase for more information
OG_FIREBASE_CLIENT_X509_CERT_URL| None | See Firebase for more information
OG_READER_VENDOR_ID | 0xffff | Vendor ID of the NFC reader
OG_READER_PRODUCT_ID | 0x0035 | Product ID of the NFC reader
OG_SLACK_MESSAGES_ENABLED | True | Send messages to Slack?
OG_SLACK_TOKEN | None | Slack token for the app
OG_SLACK_DEV_CHANNEL | #kontorspill_dev | Dev channel, debug messages and such gets posted here
OG_SLACK_CHANNEL | #kontorspill | Slack channel to post game information to
OG_SLACK_USERNAME | Kontor Spill | Username of the bot that posts to Slack
