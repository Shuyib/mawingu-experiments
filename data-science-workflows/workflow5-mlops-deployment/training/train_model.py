"""
Model training script with MLflow experiment tracking and model registry.
Trains both scikit-learn and XGBoost models for comparison.
"""

import os
import pickle
import argparse
from datetime import datetime

import mlflow
import mlflow.sklearn
import mlflow.xgboost
import numpy as np
import pandas as pd
from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from xgboost import XGBClassifier


def load_data():
    """Load and prepare the wine dataset."""
    wine = load_wine()
    X = pd.DataFrame(wine.data, columns=wine.feature_names)
    y = pd.Series(wine.target, name='target')
    
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_sklearn_model(X_train, y_train, X_test, y_test, params):
    """Train a Random Forest model with MLflow tracking."""
    
    with mlflow.start_run(run_name="sklearn_random_forest") as run:
        # Log parameters
        mlflow.log_params(params)
        
        # Train model
        model = RandomForestClassifier(**params, random_state=42)
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # Cross-validation score
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        
        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("cv_mean", cv_mean)
        mlflow.log_metric("cv_std", cv_std)
        
        # Log confusion matrix as artifact
        cm = confusion_matrix(y_test, y_pred)
        cm_df = pd.DataFrame(cm)
        cm_df.to_csv("confusion_matrix.csv", index=False)
        mlflow.log_artifact("confusion_matrix.csv")
        os.remove("confusion_matrix.csv")
        
        # Log classification report
        report = classification_report(y_test, y_pred)
        with open("classification_report.txt", "w") as f:
            f.write(report)
        mlflow.log_artifact("classification_report.txt")
        os.remove("classification_report.txt")
        
        # Log model
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name="wine_classifier_rf"
        )
        
        print(f"Random Forest - Accuracy: {accuracy:.4f}, F1: {f1:.4f}")
        return run.info.run_id, accuracy


def train_xgboost_model(X_train, y_train, X_test, y_test, params):
    """Train an XGBoost model with MLflow tracking."""
    
    with mlflow.start_run(run_name="xgboost_classifier") as run:
        # Log parameters
        mlflow.log_params(params)
        
        # Train model
        model = XGBClassifier(**params, random_state=42, eval_metric='mlogloss')
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # Cross-validation score
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        
        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("cv_mean", cv_mean)
        mlflow.log_metric("cv_std", cv_std)
        
        # Log feature importance
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        feature_importance.to_csv("feature_importance.csv", index=False)
        mlflow.log_artifact("feature_importance.csv")
        os.remove("feature_importance.csv")
        
        # Log model
        mlflow.xgboost.log_model(
            model,
            "model",
            registered_model_name="wine_classifier_xgb"
        )
        
        print(f"XGBoost - Accuracy: {accuracy:.4f}, F1: {f1:.4f}")
        return run.info.run_id, accuracy


def main():
    parser = argparse.ArgumentParser(description='Train ML models with MLflow tracking')
    parser.add_argument('--experiment-name', type=str, default='wine_classification',
                        help='MLflow experiment name')
    parser.add_argument('--model-type', type=str, choices=['sklearn', 'xgboost', 'both'],
                        default='both', help='Model type to train')
    args = parser.parse_args()
    
    # Set MLflow experiment
    mlflow.set_experiment(args.experiment_name)
    
    # Set MLflow tracking URI (use local directory if not set)
    if not os.getenv('MLFLOW_TRACKING_URI'):
        mlflow.set_tracking_uri("file:./mlruns")
    
    print("Loading data...")
    X_train, X_test, y_train, y_test = load_data()
    
    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    results = {}
    
    if args.model_type in ['sklearn', 'both']:
        print("\nTraining Random Forest model...")
        rf_params = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2
        }
        rf_run_id, rf_acc = train_sklearn_model(X_train, y_train, X_test, y_test, rf_params)
        results['random_forest'] = {'run_id': rf_run_id, 'accuracy': rf_acc}
    
    if args.model_type in ['xgboost', 'both']:
        print("\nTraining XGBoost model...")
        xgb_params = {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8
        }
        xgb_run_id, xgb_acc = train_xgboost_model(X_train, y_train, X_test, y_test, xgb_params)
        results['xgboost'] = {'run_id': xgb_run_id, 'accuracy': xgb_acc}
    
    print("\n" + "="*50)
    print("Training Complete!")
    print("="*50)
    for model_name, result in results.items():
        print(f"{model_name}: Run ID={result['run_id']}, Accuracy={result['accuracy']:.4f}")
    
    print("\nView results in MLflow UI:")
    print("  mlflow ui --backend-store-uri file:./mlruns")


if __name__ == "__main__":
    main()
