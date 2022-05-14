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
	python main.py

build:
	#build container
    	docker build -t generate_data:v0 .
	
run:
	#run docker
	docker run -e ENDPOINT_URL -e SECRET_KEY -e SPACES_ID -e SPACES_NAME generate_data:v0

deploy:
	#deploy
	
all: install post-install lint test deploy
