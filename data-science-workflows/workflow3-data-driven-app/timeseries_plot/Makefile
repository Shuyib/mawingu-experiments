install:
	pip --no-cache-dir install pipenv


post-install:
	#install commands
	pip install --upgrade pip &&\
		pipenv install --deploy --system 

clean-dir:
	rm -rf /root/.cache

format:
	#format code
	black *.py mylib/*.py

lint:
	#flake8 or #pylint
	pylint --disable=R,C *.py mylib/*.py

test:
	#test
	#python -m pytest -vv --cov=mylib --cov=main test_*.py

scripts:
	# run scripts
	python plot_timeseries.py
	
build:
	#build container
    docker build -t plot_timeseries:v0 .
run:
	#run docker in detached mode add -d flag
	docker run -e ENDPOINT_URL -e SECRET_KEY -e SPACES_ID -e SPACES_NAME plot-timeseries-app:v0
deploy:
	#deploy
	docker tag <my-image> registry.digitalocean.com/<my-registry>/<my-image>
	docker push registry.digitalocean.com/<my-registry>/<my-image>  

all: install post-install lint test deploy
