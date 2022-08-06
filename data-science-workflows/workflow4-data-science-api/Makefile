install:
	#install commands
	pip --no-cache-dir install --upgrade pip &&\
		pip --no-cache-dir install -r requirements.txt

docstring:
	# format docstring
	pyment -w -o numpydoc *.py
	

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
	python app.py

build:
	#build container
	docker build -t workflow4-data-science-api .
	
run:
	#run docker
	docker run -p 5000:5000 -v workflow4-data-science-api

push:
	# move to the docker registry
	docker tag <my-image> registry.digitalocean.com/<my-registry>/<my-image:version e.g v0>
	docker push registry.digitalocean.com/<my-registry>/<my-image:version e.g v0>

deploy:
	# run the container in pod
	kubectl create -f deployments.yaml
	

all: install post-install lint test build run push 
