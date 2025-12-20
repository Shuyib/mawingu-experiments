"""
FastAPI inference service for model predictions.
Supports real-time inference, batch predictions, and A/B testing.
"""

import os
import time
import pickle
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

import mlflow
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, validator


# Pydantic models for request/response validation
class WineFeatures(BaseModel):
    """Wine classification features."""
    alcohol: float = Field(..., description="Alcohol content", ge=0, le=20)
    malic_acid: float = Field(..., description="Malic acid", ge=0)
    ash: float = Field(..., description="Ash content", ge=0)
    alcalinity_of_ash: float = Field(..., description="Alcalinity of ash", ge=0)
    magnesium: float = Field(..., description="Magnesium content", ge=0)
    total_phenols: float = Field(..., description="Total phenols", ge=0)
    flavanoids: float = Field(..., description="Flavanoids", ge=0)
    nonflavanoid_phenols: float = Field(..., description="Nonflavanoid phenols", ge=0)
    proanthocyanins: float = Field(..., description="Proanthocyanins", ge=0)
    color_intensity: float = Field(..., description="Color intensity", ge=0)
    hue: float = Field(..., description="Hue", ge=0)
    od280_od315_of_diluted_wines: float = Field(..., description="OD280/OD315 of diluted wines", ge=0)
    proline: float = Field(..., description="Proline content", ge=0)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame for model input with correct column order."""
        # Use the exact column order from sklearn's wine dataset
        columns = [
            'alcohol', 'malic_acid', 'ash', 'alcalinity_of_ash', 
            'magnesium', 'total_phenols', 'flavanoids', 'nonflavanoid_phenols',
            'proanthocyanins', 'color_intensity', 'hue', 
            'od280/od315_of_diluted_wines', 'proline'
        ]
        
        data = {
            'alcohol': self.alcohol,
            'malic_acid': self.malic_acid,
            'ash': self.ash,
            'alcalinity_of_ash': self.alcalinity_of_ash,
            'magnesium': self.magnesium,
            'total_phenols': self.total_phenols,
            'flavanoids': self.flavanoids,
            'nonflavanoid_phenols': self.nonflavanoid_phenols,
            'proanthocyanins': self.proanthocyanins,
            'color_intensity': self.color_intensity,
            'hue': self.hue,
            'od280/od315_of_diluted_wines': self.od280_od315_of_diluted_wines,
            'proline': self.proline
        }
        
        return pd.DataFrame([data], columns=columns)


class PredictionRequest(BaseModel):
    """Single prediction request."""
    features: WineFeatures
    model_version: Optional[str] = Field(None, description="Specific model version to use")


class BatchPredictionRequest(BaseModel):
    """Batch prediction request."""
    instances: List[WineFeatures]
    model_version: Optional[str] = Field(None, description="Specific model version to use")


class PredictionResponse(BaseModel):
    """Prediction response."""
    prediction: int
    probabilities: List[float]
    model_version: str
    prediction_time_ms: float
    timestamp: str


class BatchPredictionResponse(BaseModel):
    """Batch prediction response."""
    predictions: List[PredictionResponse]
    total_predictions: int
    total_time_ms: float


class ModelType(str, Enum):
    """Available model types."""
    RANDOM_FOREST = "random_forest"
    XGBOOST = "xgboost"


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    models_loaded: Dict[str, bool]
    timestamp: str


# Initialize FastAPI app
app = FastAPI(
    title="Wine Classification API",
    description="Production-ready ML inference API with MLflow integration",
    version="1.0.0"
)


# Model registry
class ModelRegistry:
    """Manages multiple model versions for A/B testing."""
    
    def __init__(self):
        self.models = {}
        self.default_model = None
        self.prediction_counts = {}
        
    def load_model(self, model_name: str, model_uri: str):
        """Load a model from MLflow."""
        try:
            model = mlflow.pyfunc.load_model(model_uri)
            self.models[model_name] = model
            self.prediction_counts[model_name] = 0
            print(f"Loaded model: {model_name} from {model_uri}")
            
            if self.default_model is None:
                self.default_model = model_name
                
            return True
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            return False
    
    def get_model(self, model_name: Optional[str] = None):
        """Get a model by name or return default."""
        if model_name is None:
            model_name = self.default_model
            
        if model_name not in self.models:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
            
        return self.models[model_name], model_name
    
    def predict(self, model_name: Optional[str], features: pd.DataFrame):
        """Make prediction with specified or default model."""
        model, used_model_name = self.get_model(model_name)
        self.prediction_counts[used_model_name] += 1
        
        # Make prediction
        prediction = model.predict(features)
        
        # Get prediction probabilities
        try:
            # For MLflow pyfunc models, we need to use the underlying model
            if hasattr(model, '_model_impl'):
                underlying_model = model._model_impl.python_model
                if hasattr(underlying_model, 'predict_proba'):
                    probabilities = underlying_model.predict_proba(features)
                    probabilities = probabilities[0].tolist()
                else:
                    probabilities = [1.0 if i == int(prediction[0]) else 0.0 for i in range(3)]
            else:
                # Direct sklearn model
                probabilities = model.predict_proba(features)
                probabilities = probabilities[0].tolist()
        except Exception as e:
            print(f"Could not get probabilities: {e}")
            # Return dummy probabilities
            probabilities = [1.0 if i == int(prediction[0]) else 0.0 for i in range(3)]
        
        return int(prediction[0]), probabilities, used_model_name


# Initialize model registry
registry = ModelRegistry()


@app.on_event("startup")
async def startup_event():
    """Load models on startup."""
    print("Starting Wine Classification API...")
    
    # Set MLflow tracking URI
    mlflow_uri = os.getenv('MLFLOW_TRACKING_URI', 'file:./mlruns')
    mlflow.set_tracking_uri(mlflow_uri)
    
    # Load default models (latest versions)
    # In production, these would be loaded from model registry
    model_path = os.getenv('MODEL_PATH', './models')
    
    # Try to load models from MLflow registry
    try:
        # Load Random Forest model
        rf_model_uri = "models:/wine_classifier_rf/latest"
        registry.load_model("random_forest", rf_model_uri)
    except Exception as e:
        print(f"Could not load RF model from registry: {e}")
    
    try:
        # Load XGBoost model
        xgb_model_uri = "models:/wine_classifier_xgb/latest"
        registry.load_model("xgboost", xgb_model_uri)
    except Exception as e:
        print(f"Could not load XGBoost model from registry: {e}")
    
    # If no models loaded from registry, try local path
    if len(registry.models) == 0:
        print("No models loaded from registry, checking local path...")
        if os.path.exists(f"{model_path}/model.pkl"):
            with open(f"{model_path}/model.pkl", "rb") as f:
                model = pickle.load(f)
                registry.models["default"] = model
                registry.default_model = "default"
                print("Loaded default model from local file")
    
    if len(registry.models) == 0:
        print("WARNING: No models loaded! Please train models first.")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Wine Classification API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "batch_predict": "/predict/batch",
            "models": "/models",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        models_loaded={name: True for name in registry.models.keys()},
        timestamp=datetime.now().isoformat()
    )


@app.get("/models")
async def list_models():
    """List available models and their prediction counts."""
    return {
        "models": list(registry.models.keys()),
        "default_model": registry.default_model,
        "prediction_counts": registry.prediction_counts
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make a single prediction.
    
    Supports A/B testing by allowing model version specification.
    """
    start_time = time.time()
    
    # Convert features to DataFrame
    features_df = request.features.to_dataframe()
    
    # Make prediction
    try:
        prediction, probabilities, model_used = registry.predict(
            request.model_version,
            features_df
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
    
    # Calculate prediction time
    prediction_time = (time.time() - start_time) * 1000  # Convert to ms
    
    return PredictionResponse(
        prediction=prediction,
        probabilities=probabilities,
        model_version=model_used,
        prediction_time_ms=round(prediction_time, 2),
        timestamp=datetime.now().isoformat()
    )


@app.post("/predict/batch", response_model=BatchPredictionResponse)
async def batch_predict(request: BatchPredictionRequest):
    """
    Make batch predictions.
    
    More efficient for multiple predictions at once.
    """
    start_time = time.time()
    
    predictions = []
    for features in request.instances:
        pred_start = time.time()
        features_df = features.to_dataframe()
        
        try:
            prediction, probabilities, model_used = registry.predict(
                request.model_version,
                features_df
            )
            
            pred_time = (time.time() - pred_start) * 1000
            
            predictions.append(PredictionResponse(
                prediction=prediction,
                probabilities=probabilities,
                model_version=model_used,
                prediction_time_ms=round(pred_time, 2),
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")
    
    total_time = (time.time() - start_time) * 1000
    
    return BatchPredictionResponse(
        predictions=predictions,
        total_predictions=len(predictions),
        total_time_ms=round(total_time, 2)
    )


@app.post("/ab-test/route")
async def ab_test_route(request: PredictionRequest, traffic_split: Dict[str, float] = None):
    """
    Route predictions for A/B testing based on traffic split.
    
    Example traffic_split: {"random_forest": 0.7, "xgboost": 0.3}
    """
    if traffic_split is None:
        traffic_split = {"random_forest": 0.5, "xgboost": 0.5}
    
    # Randomly select model based on traffic split
    models = list(traffic_split.keys())
    weights = list(traffic_split.values())
    
    selected_model = np.random.choice(models, p=weights)
    request.model_version = selected_model
    
    return await predict(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
