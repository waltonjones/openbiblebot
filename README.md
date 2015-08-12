# OpenBibleBot

This is a Telegram bot that serves up scripture in both English and Korean using the [XML Bible API](http://www.4-14.org.uk/xml-bible-web-service-api).

It uses the excellent [python-telegram-bot](https://github.com/leandrotoledo/python-telegram-bot) wrapper for the Telegram API. 

I implemented this bot using the webhook method and I am currently hosting it on [Webfaction](https://www.webfaction.com/?aid=34111). To get this set up correctly, I used Webfaction's recommended [bash script](https://community.webfaction.com/questions/12718/installing-flask).

Finally, Telegram also requires an active SSL certificate that is signed by a third-party.