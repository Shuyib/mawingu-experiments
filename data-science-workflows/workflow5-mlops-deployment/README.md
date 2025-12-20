# Workflow 5: MLOps - Production Model Deployment

This workflow demonstrates a complete MLOps pipeline for deploying machine learning models to production, including experiment tracking, model registry, containerization, deployment, monitoring, and A/B testing.

## 🎯 Overview

This project showcases production-grade ML deployment with:
- **Model Training**: scikit-learn and XGBoost implementations
- **Experiment Tracking**: MLflow for tracking experiments and model versioning
- **Model Registry**: Centralized model versioning and lifecycle management
- **Containerization**: Docker images for training and inference
- **Deployment**: FastAPI inference service with health checks
- **Monitoring**: Data drift detection and model performance tracking
- **A/B Testing**: Traffic splitting between model versions
- **Orchestration**: Docker Compose and Kubernetes manifests

## 📁 Project Structure

```
workflow5-mlops-deployment/
├── training/
│   └── train_model.py          # Model training with MLflow
├── inference/
│   └── app.py                  # FastAPI inference service
├── monitoring/
│   └── monitor.py              # Drift detection and monitoring
├── data/                       # Training data (auto-generated)
├── models/                     # Saved models
├── mlruns/                     # MLflow tracking data
├── notebooks/                  # Jupyter notebooks for exploration
├── requirements.txt            # Python dependencies
├── Dockerfile.training         # Docker image for training
├── Dockerfile.inference        # Docker image for inference
├── docker-compose.yml          # Full stack orchestration
├── k8s-deployment.yaml         # Kubernetes manifests
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- (Optional) Kubernetes cluster for production deployment

### 1. Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Train Models Locally

```bash
# Train both Random Forest and XGBoost models
python training/train_model.py --model-type both

# Train specific model
python training/train_model.py --model-type sklearn
python training/train_model.py --model-type xgboost

# View experiments in MLflow UI
mlflow ui --backend-store-uri file:./mlruns
# Open http://localhost:5000
```

### 3. Run Inference Service Locally

```bash
# Start FastAPI server
cd inference
python app.py

# Or use uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Test the API:
```bash
# Health check
curl http://localhost:8000/health

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "alcohol": 13.5,
      "malic_acid": 2.3,
      "ash": 2.4,
      "alcalinity_of_ash": 19.0,
      "magnesium": 100.0,
      "total_phenols": 2.8,
      "flavanoids": 2.6,
      "nonflavanoid_phenols": 0.3,
      "proanthocyanins": 1.9,
      "color_intensity": 5.5,
      "hue": 1.0,
      "od280_od315_of_diluted_wines": 3.1,
      "proline": 1000.0
    }
  }'
```

### 4. Run Model Monitoring

```bash
# Generate drift and performance reports
python monitoring/monitor.py
```

## 🐳 Docker Deployment

### Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services available:
- MLflow UI: http://localhost:5000
- Inference API (RF): http://localhost:8001
- Inference API (XGBoost): http://localhost:8002

### Build Individual Images

```bash
# Build training image
docker build -f Dockerfile.training -t mlops-training:latest .

# Build inference image
docker build -f Dockerfile.inference -t mlops-inference:latest .

# Run training
docker run -v $(pwd)/mlruns:/app/mlruns -v $(pwd)/models:/app/models mlops-training:latest

# Run inference
docker run -p 8000:8000 -v $(pwd)/mlruns:/app/mlruns mlops-inference:latest
```

## ☸️ Kubernetes Deployment

### Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s-deployment.yaml

# Check deployments
kubectl get deployments
kubectl get pods
kubectl get services

# View MLflow service
kubectl get service mlflow-service

# View inference service
kubectl get service inference-service

# Scale inference service
kubectl scale deployment inference-service --replicas=5

# View autoscaling
kubectl get hpa inference-hpa
```

### Access Services

```bash
# Port forward MLflow
kubectl port-forward service/mlflow-service 5000:5000

# Port forward inference API
kubectl port-forward service/inference-service 8000:80
```

## 📊 MLflow Model Registry

### Register Models

Models are automatically registered during training with versioning:

```python
# In training script
mlflow.sklearn.log_model(
    model,
    "model",
    registered_model_name="wine_classifier_rf"
)
```

### Promote Models

Use MLflow UI or Python API to promote models:

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Transition model to production
client.transition_model_version_stage(
    name="wine_classifier_rf",
    version=1,
    stage="Production"
)
```

## 🧪 A/B Testing

The inference service supports A/B testing with traffic splitting:

```bash
# Route 70% traffic to Random Forest, 30% to XGBoost
curl -X POST http://localhost:8000/ab-test/route \
  -H "Content-Type: application/json" \
  -d '{
    "features": {...},
    "traffic_split": {
      "random_forest": 0.7,
      "xgboost": 0.3
    }
  }'
```

## 📈 Model Monitoring

### Data Drift Detection

The monitoring module uses Evidently to detect data drift:

```python
from monitoring.monitor import ModelMonitor

# Initialize monitor with reference data
monitor = ModelMonitor(reference_data)

# Check for drift in production data
drift_metrics = monitor.generate_data_drift_report(current_data)

# Alert if drift detected
if drift_metrics['dataset_drift']:
    print(f"⚠️  Drift detected: {drift_metrics['drift_share']:.2%}")
```

### Performance Monitoring

Track model performance over time:

```python
# Generate performance report
perf_metrics = monitor.generate_model_performance_report(
    current_data,
    predictions,
    ground_truth  # Optional
)
```

Reports are saved as HTML in the `monitoring/` directory.

## 🔧 API Documentation

Once the inference service is running, access interactive API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/models` | GET | List available models |
| `/predict` | POST | Single prediction |
| `/predict/batch` | POST | Batch predictions |
| `/ab-test/route` | POST | A/B testing endpoint |

## 📝 Example Usage

### Single Prediction

```python
import requests

url = "http://localhost:8000/predict"
data = {
    "features": {
        "alcohol": 13.5,
        "malic_acid": 2.3,
        "ash": 2.4,
        "alcalinity_of_ash": 19.0,
        "magnesium": 100.0,
        "total_phenols": 2.8,
        "flavanoids": 2.6,
        "nonflavanoid_phenols": 0.3,
        "proanthocyanins": 1.9,
        "color_intensity": 5.5,
        "hue": 1.0,
        "od280_od315_of_diluted_wines": 3.1,
        "proline": 1000.0
    },
    "model_version": "random_forest"
}

response = requests.post(url, json=data)
print(response.json())
```

### Batch Prediction

```python
url = "http://localhost:8000/predict/batch"
data = {
    "instances": [
        {"alcohol": 13.5, "malic_acid": 2.3, ...},
        {"alcohol": 14.2, "malic_acid": 1.8, ...},
    ]
}

response = requests.post(url, json=data)
print(response.json())
```

## 🔐 Best Practices

### Security
- Use environment variables for sensitive configuration
- Implement authentication for production APIs
- Secure MLflow tracking server with authentication
- Use secrets management (Kubernetes Secrets, AWS Secrets Manager)

### Monitoring
- Set up alerting for drift detection
- Monitor API latency and throughput
- Track model performance metrics
- Log predictions for analysis

### Model Lifecycle
- Version all models in MLflow registry
- Use staging environments before production
- Implement rollback mechanisms
- Regular model retraining schedule

### Scalability
- Use Kubernetes HPA for auto-scaling
- Implement caching for frequently used predictions
- Use async processing for batch predictions
- Monitor resource utilization

## 🧰 Technologies Used

- **ML Frameworks**: scikit-learn, XGBoost
- **Experiment Tracking**: MLflow
- **API Framework**: FastAPI
- **Monitoring**: Evidently
- **Containerization**: Docker
- **Orchestration**: Docker Compose, Kubernetes
- **Data Validation**: Great Expectations

## 🔄 CI/CD Integration

For production deployment, integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: MLOps Pipeline

on:
  push:
    branches: [main]

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Train Model
        run: |
          pip install -r requirements.txt
          python training/train_model.py
      
  build:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker Image
        run: docker build -f Dockerfile.inference -t inference:${{ github.sha }} .
      
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: kubectl apply -f k8s-deployment.yaml
```

## 🐛 Troubleshooting

### MLflow Connection Issues
```bash
# Check MLflow server is running
curl http://localhost:5000/health

# Set tracking URI explicitly
export MLFLOW_TRACKING_URI=http://localhost:5000
```

### Model Loading Errors
```bash
# Verify model exists in registry
mlflow models list

# Check model path permissions
ls -la models/
```

### Docker Issues
```bash
# Remove old containers
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# View container logs
docker-compose logs inference-rf
```

## 📚 Additional Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Evidently Documentation](https://docs.evidentlyai.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## 🤝 Contributing

This is a demonstration project. Adapt and extend based on your use case:
- Add more sophisticated models
- Implement feature stores
- Add data versioning with DVC
- Integrate with cloud providers (AWS SageMaker, Azure ML, GCP Vertex AI)
- Add authentication and authorization
- Implement canary deployments

## 📄 License

This project follows the same license as the parent repository (CC0-1.0).

## 🎓 Learning Outcomes

By working through this workflow, you'll understand:
- ✅ Setting up MLflow for experiment tracking
- ✅ Building production-ready model training pipelines
- ✅ Creating REST APIs for model inference
- ✅ Containerizing ML applications
- ✅ Deploying to Kubernetes
- ✅ Implementing model monitoring and drift detection
- ✅ A/B testing for model versions
- ✅ MLOps best practices and patterns

---

**Why This Matters**: Companies need to move models from notebooks to production. This workflow demonstrates the complete MLOps lifecycle, from training to deployment to monitoring, using industry-standard tools and practices.
