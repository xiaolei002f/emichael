.PHONY: start kill update clean update

start: kill
	nohup python LatexServer.py </dev/null >> /var/log/latexbot/latexbot.log 2>&1

update: kill
	git pull

kill:
	ps -ef | grep "LatexServer.py" | grep -v grep | awk '{print $$2}' | xargs kill -15
