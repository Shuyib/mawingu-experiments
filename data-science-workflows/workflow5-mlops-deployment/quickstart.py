#!/usr/bin/env python
"""
MLOps Workflow Quick Start Demo

This script demonstrates the complete MLOps workflow:
1. Train models with MLflow tracking
2. Load models from registry
3. Make predictions via API
4. Monitor model performance

Run this to see the full workflow in action!
"""

import time
import requests
import subprocess
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'


def print_step(step_num, description):
    """Print a workflow step."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{GREEN}Step {step_num}: {description}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def run_command(command, description):
    """Run a shell command and display output."""
    print(f"{YELLOW}Running: {description}{RESET}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"{RED}Error: {result.stderr}{RESET}")
        return False
    print(result.stdout)
    return True


def check_api_health():
    """Check if API is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}MLOps Workflow Demo{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    
    # Step 1: Train models
    print_step(1, "Training ML Models with MLflow")
    print("Training both Random Forest and XGBoost models...")
    
    success = run_command(
        "python training/train_model.py --model-type both",
        "Model Training"
    )
    
    if not success:
        print(f"{RED}Training failed. Please check the error messages above.{RESET}")
        return 1
    
    print(f"{GREEN}✓ Models trained successfully!{RESET}")
    
    # Step 2: View MLflow experiments
    print_step(2, "MLflow Experiment Tracking")
    print("Models and metrics have been logged to MLflow.")
    print(f"\n{YELLOW}To view the MLflow UI, run:{RESET}")
    print(f"  mlflow ui --backend-store-uri file:./mlruns")
    print(f"  Then open: http://localhost:5000\n")
    
    # Step 3: Start inference API
    print_step(3, "Starting Inference API")
    print("Starting FastAPI inference server...")
    
    if check_api_health():
        print(f"{YELLOW}API is already running!{RESET}")
    else:
        print(f"{YELLOW}Starting API in background...{RESET}")
        print("(In production, use: uvicorn inference.app:app --host 0.0.0.0 --port 8000)")
        print(f"{YELLOW}Note: For this demo, start the API manually in another terminal{RESET}")
        print(f"{YELLOW}Command: python -m uvicorn inference.app:app --reload{RESET}\n")
        time.sleep(2)
    
    # Step 4: Test predictions
    print_step(4, "Making Predictions")
    
    sample_data = {
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
    }
    
    if check_api_health():
        print("API is ready! Making sample prediction...")
        
        try:
            # Test health endpoint
            response = requests.get("http://localhost:8000/health")
            print(f"\n{GREEN}Health Check:{RESET}")
            print(response.json())
            
            # Test models endpoint
            response = requests.get("http://localhost:8000/models")
            print(f"\n{GREEN}Available Models:{RESET}")
            print(response.json())
            
            # Test prediction
            response = requests.post(
                "http://localhost:8000/predict",
                json=sample_data
            )
            result = response.json()
            
            print(f"\n{GREEN}Prediction Result:{RESET}")
            print(f"  Predicted Class: {result.get('prediction')}")
            print(f"  Confidence: {max(result.get('probabilities', [0])):.2%}")
            print(f"  Model Used: {result.get('model_version')}")
            print(f"  Prediction Time: {result.get('prediction_time_ms')}ms")
            
            print(f"\n{GREEN}✓ Predictions working!{RESET}")
            
        except Exception as e:
            print(f"{RED}Error making prediction: {e}{RESET}")
            print(f"{YELLOW}Make sure the API is running!{RESET}")
    else:
        print(f"{YELLOW}API is not running. Start it with:{RESET}")
        print(f"  python -m uvicorn inference.app:app --reload")
        print(f"\n{YELLOW}Then run this script again to test predictions.{RESET}")
    
    # Step 5: Model monitoring
    print_step(5, "Model Monitoring")
    print("Generating drift detection report...")
    
    success = run_command(
        "python monitoring/monitor.py",
        "Drift Detection"
    )
    
    if success:
        print(f"{GREEN}✓ Monitoring reports generated!{RESET}")
        print(f"\nCheck the {YELLOW}monitoring/{RESET} directory for HTML reports.")
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{GREEN}Demo Complete!{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    print(f"{GREEN}What you've learned:{RESET}")
    print("  ✓ Model training with MLflow tracking")
    print("  ✓ Model registry and versioning")
    print("  ✓ FastAPI inference service")
    print("  ✓ Real-time predictions")
    print("  ✓ Model monitoring and drift detection")
    
    print(f"\n{GREEN}Next Steps:{RESET}")
    print("  1. View MLflow UI: mlflow ui --backend-store-uri file:./mlruns")
    print("  2. Explore the API docs: http://localhost:8000/docs")
    print("  3. Try the Jupyter notebook: notebooks/mlops_demo.ipynb")
    print("  4. Deploy with Docker: docker-compose up")
    print("  5. Deploy to Kubernetes: kubectl apply -f k8s-deployment.yaml")
    
    print(f"\n{YELLOW}For more information, see README.md{RESET}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
