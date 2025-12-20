"""
Tests for the MLOps workflow components.
"""

import pytest
import pandas as pd
import numpy as np
from sklearn.datasets import load_wine


def test_wine_dataset_loads():
    """Test that wine dataset can be loaded."""
    wine = load_wine()
    assert wine.data.shape[0] > 0
    assert wine.data.shape[1] == 13
    assert len(wine.target_names) == 3


def test_features_dataframe_creation():
    """Test creating features dataframe."""
    wine = load_wine()
    X = pd.DataFrame(wine.data, columns=wine.feature_names)
    
    assert isinstance(X, pd.DataFrame)
    assert len(X.columns) == 13
    assert X.shape[0] == wine.data.shape[0]


def test_model_input_format():
    """Test that model input format is correct."""
    wine = load_wine()
    X = pd.DataFrame(wine.data, columns=wine.feature_names)
    
    # Test single sample
    sample = X.iloc[0:1]
    assert sample.shape == (1, 13)
    
    # Test batch
    batch = X.iloc[0:10]
    assert batch.shape == (10, 13)


def test_target_classes():
    """Test that target has correct number of classes."""
    wine = load_wine()
    unique_targets = np.unique(wine.target)
    
    assert len(unique_targets) == 3
    assert all(t in [0, 1, 2] for t in unique_targets)


# API Tests (require running server)
@pytest.mark.api
def test_api_health_endpoint():
    """Test API health endpoint (requires running server)."""
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    except requests.exceptions.RequestException:
        pytest.skip("API server not running")


@pytest.mark.api
def test_api_models_endpoint():
    """Test API models endpoint (requires running server)."""
    import requests
    try:
        response = requests.get("http://localhost:8000/models", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
    except requests.exceptions.RequestException:
        pytest.skip("API server not running")


@pytest.mark.api
def test_api_prediction_endpoint():
    """Test API prediction endpoint (requires running server)."""
    import requests
    
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
    
    try:
        response = requests.post(
            "http://localhost:8000/predict",
            json=sample_data,
            timeout=5
        )
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "probabilities" in data
        assert data["prediction"] in [0, 1, 2]
    except requests.exceptions.RequestException:
        pytest.skip("API server not running")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
