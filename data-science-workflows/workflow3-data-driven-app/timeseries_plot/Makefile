PLATFORM=linux/amd64

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

run_scripts:
	# run scripts
	python plot_timeseries.py
	
build:
	#build container
    sudo docker build --platform $(PLATFORM) -t plot_timeseries:v0 .
run:
	#run docker in detached mode add -d flag
	sudo docker run --platform $(PLATFORM) -e ENDPOINT_URL=${ENDPOINT_URL} -e SECRET_KEY=${SECRET_KEY} -e SPACES_ID=${SPACES_ID} -e SPACES_NAME=${SPACES_NAME} plot_timeseries:v0
push:
	# move to the docker registry
	# Here are examples
	docker tag <my-image> registry.digitalocean.com/<my-registry>/<my-image:version e.g v0>
	docker push registry.digitalocean.com/<my-registry>/<my-image:version e.g v0>

deploy:
	kubectl create -f deployments.yaml


all: install post-install lint test build run push
