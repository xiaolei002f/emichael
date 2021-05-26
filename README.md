# Slack Latex Bot

A simple bot that takes in Latex equations in the URL and returns the
corresponding png image.

To run, either use the Makefile and run `make start` (you'll have to set your
hostname in that file) or run the `LatexServer.py` script directly. You will
also have to configure your Slack instance to talk to  the bot. To do this, go
to  `yourinstance.slack.com/apps/manage/custom-integrations` and add a slash
command configuration. Set the Command to `/latex`, and set the URL to
`http://YOURLATEXBOTHOSTNAME:PORT/`. The Method should be `POST`.
