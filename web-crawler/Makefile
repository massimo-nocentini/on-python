

step-one:
	rm fetched/*.json
	python3.6 non-blocking-sockets-tight-loop.py 

step-two:
	rm fetched/*.json
	python3.6 non-blocking-sockets-selectors.py 

step-three:
	rm fetched/*.json
	python3.6 non-blocking-sockets-fetcher.py 

step-four:
	rm fetched/*.json
	python3.6 fetcher-with-futures.py 

step-five:
	rm fetched/*.json
	python3.6 fetcher-with-yield-from.py 

step-five-half:
	rm fetched/*.json
	python3.6 fetcher-with-async-await.py 

step-six:
	rm fetched/*.json
	python3.6 crawling.py 

step-six-half:
	python3.6 crawling-with-async-await.py 
