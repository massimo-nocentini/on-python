

step-one:
	rm -f fetched/*.json
	python3.6 non-blocking-sockets-tight-loop.py 

step-two:
	rm -f fetched/*.json
	python3.6 non-blocking-sockets-selectors.py 

step-three:
	rm -f fetched/*.json
	python3.6 non-blocking-sockets-fetcher.py 

step-four:
	rm -f fetched/*.json
	python3.6 fetcher-with-futures.py 

step-five:
	rm -f fetched/*.json
	python3.6 fetcher-with-yield-from.py 

step-five-half:
	rm -f fetched/*.json
	python3.6 fetcher-with-async-await.py 

step-six:
	rm -f fetched/*.json
	python3.6 crawling.py 

step-six-half:
	python3.6 crawling-with-async-await.py 
