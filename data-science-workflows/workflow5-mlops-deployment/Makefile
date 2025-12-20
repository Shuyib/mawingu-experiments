.PHONY: help install train serve monitor docker-build docker-up docker-down k8s-deploy k8s-delete test clean

# Default target
help:
	@echo "MLOps Workflow - Available Commands:"
	@echo ""
	@echo "  make install        - Install Python dependencies"
	@echo "  make train          - Train models with MLflow"
	@echo "  make serve          - Start FastAPI inference server"
	@echo "  make mlflow-ui      - Start MLflow UI"
	@echo "  make monitor        - Run model monitoring"
	@echo ""
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-up      - Start all services with Docker Compose"
	@echo "  make docker-down    - Stop Docker Compose services"
	@echo "  make docker-logs    - View Docker Compose logs"
	@echo ""
	@echo "  make k8s-deploy     - Deploy to Kubernetes"
	@echo "  make k8s-delete     - Delete Kubernetes deployment"
	@echo "  make k8s-status     - Check Kubernetes deployment status"
	@echo ""
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean generated files"

# Install dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# Train models
train:
	python training/train_model.py --model-type both

# Train specific model
train-rf:
	python training/train_model.py --model-type sklearn

train-xgb:
	python training/train_model.py --model-type xgboost

# Start inference server
serve:
	uvicorn inference.app:app --host 0.0.0.0 --port 8000 --reload

# Start MLflow UI
mlflow-ui:
	mlflow ui --backend-store-uri file:./mlruns --port 5000

# Run monitoring
monitor:
	python monitoring/monitor.py

# Docker commands
docker-build:
	docker build -f Dockerfile.training -t mlops-training:latest .
	docker build -f Dockerfile.inference -t mlops-inference:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

# Kubernetes commands
k8s-deploy:
	kubectl apply -f k8s-deployment.yaml

k8s-delete:
	kubectl delete -f k8s-deployment.yaml

k8s-status:
	@echo "Deployments:"
	@kubectl get deployments
	@echo "\nPods:"
	@kubectl get pods
	@echo "\nServices:"
	@kubectl get services
	@echo "\nHPA:"
	@kubectl get hpa

k8s-logs-inference:
	kubectl logs -l app=inference --tail=100 -f

k8s-logs-mlflow:
	kubectl logs -l app=mlflow --tail=100 -f

# Testing
test:
	pytest -v

test-api:
	@echo "Testing health endpoint..."
	@curl -s http://localhost:8000/health | python -m json.tool
	@echo "\nTesting models endpoint..."
	@curl -s http://localhost:8000/models | python -m json.tool

# Clean up
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf *.pyc
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-all: clean
	rm -rf mlruns
	rm -rf models
	rm -rf monitoring/*.html
	rm -rf monitoring/*.json

# Development helpers
format:
	black training/ inference/ monitoring/

lint:
	flake8 training/ inference/ monitoring/

# Quick start for new users
quickstart: install train mlflow-ui

# Production deployment
prod-deploy: docker-build docker-up

# Full stack local development
dev: install train serve
