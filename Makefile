.PHONY: start kill update clean update

HOSTNAME=yourserverhostname.com

start: kill
	nohup python LatexServer.py -H $(HOSTNAME) </dev/null >> /var/log/latexbot/latexbot.log 2>&1

update: kill
	git pull

kill:
	ps -ef | grep "LatexServer.py" | grep -v grep | awk '{print $$2}' | xargs kill -15
