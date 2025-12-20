"""
Model monitoring and drift detection using Evidently.
Tracks model performance and data drift over time.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from evidently.report import Report
from evidently.metric_preset import (
    DataDriftPreset,
    DataQualityPreset,
    TargetDriftPreset,
    ClassificationPreset
)
from evidently.metrics import (
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
    ColumnDriftMetric
)


class ModelMonitor:
    """Monitor model performance and detect data drift."""
    
    def __init__(self, reference_data: pd.DataFrame, output_dir: str = "./monitoring"):
        """
        Initialize model monitor.
        
        Args:
            reference_data: Reference dataset (training data)
            output_dir: Directory to save monitoring reports
        """
        self.reference_data = reference_data
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.drift_history = []
        
    def generate_data_drift_report(
        self,
        current_data: pd.DataFrame,
        save_html: bool = True
    ) -> Dict[str, Any]:
        """
        Generate data drift report comparing current data to reference.
        
        Args:
            current_data: Current production data
            save_html: Whether to save HTML report
            
        Returns:
            Dictionary with drift metrics
        """
        # Create report
        report = Report(metrics=[
            DataDriftPreset(),
            DataQualityPreset()
        ])
        
        # Run report
        report.run(
            reference_data=self.reference_data,
            current_data=current_data
        )
        
        # Save HTML report
        if save_html:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_path = self.output_dir / f"data_drift_report_{timestamp}.html"
            report.save_html(str(html_path))
            print(f"Drift report saved to: {html_path}")
        
        # Extract metrics
        report_dict = report.as_dict()
        
        # Parse drift results
        drift_metrics = {
            "timestamp": datetime.now().isoformat(),
            "dataset_drift": False,
            "n_drifted_features": 0,
            "drift_share": 0.0,
            "drifted_features": []
        }
        
        # Extract drift information from report
        for metric in report_dict.get("metrics", []):
            if metric.get("metric") == "DatasetDriftMetric":
                result = metric.get("result", {})
                drift_metrics["dataset_drift"] = result.get("dataset_drift", False)
                drift_metrics["drift_share"] = result.get("drift_share", 0.0)
                drift_metrics["n_drifted_features"] = result.get("number_of_drifted_columns", 0)
                
                # Get drifted feature names
                drift_by_columns = result.get("drift_by_columns", {})
                drift_metrics["drifted_features"] = [
                    col for col, info in drift_by_columns.items()
                    if info.get("drift_detected", False)
                ]
        
        # Save metrics to JSON
        metrics_path = self.output_dir / f"drift_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_path, "w") as f:
            json.dump(drift_metrics, f, indent=2)
        
        # Add to history
        self.drift_history.append(drift_metrics)
        
        return drift_metrics
    
    def generate_model_performance_report(
        self,
        current_data: pd.DataFrame,
        current_predictions: np.ndarray,
        current_targets: Optional[np.ndarray] = None,
        save_html: bool = True
    ) -> Dict[str, Any]:
        """
        Generate model performance report.
        
        Args:
            current_data: Current production data
            current_predictions: Model predictions
            current_targets: Actual target values (if available)
            save_html: Whether to save HTML report
            
        Returns:
            Dictionary with performance metrics
        """
        # Add predictions to dataframe
        current_df = current_data.copy()
        current_df['prediction'] = current_predictions
        
        if current_targets is not None:
            current_df['target'] = current_targets
            
            # Create classification report with targets
            report = Report(metrics=[
                ClassificationPreset(),
                TargetDriftPreset()
            ])
            
            reference_df = self.reference_data.copy()
            if 'prediction' not in reference_df.columns:
                # Assume reference has targets
                reference_df['prediction'] = reference_df.get('target', 0)
            
            report.run(
                reference_data=reference_df,
                current_data=current_df
            )
        else:
            # Only prediction drift (no ground truth)
            report = Report(metrics=[
                TargetDriftPreset()
            ])
            
            reference_df = self.reference_data.copy()
            if 'prediction' not in reference_df.columns:
                reference_df['prediction'] = reference_df.get('target', 0)
            
            report.run(
                reference_data=reference_df,
                current_data=current_df
            )
        
        # Save HTML report
        if save_html:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_path = self.output_dir / f"model_performance_report_{timestamp}.html"
            report.save_html(str(html_path))
            print(f"Performance report saved to: {html_path}")
        
        # Extract metrics
        report_dict = report.as_dict()
        
        performance_metrics = {
            "timestamp": datetime.now().isoformat(),
            "has_ground_truth": current_targets is not None,
            "n_predictions": len(current_predictions)
        }
        
        # Add accuracy if ground truth available
        if current_targets is not None:
            from sklearn.metrics import accuracy_score, f1_score
            performance_metrics["accuracy"] = float(accuracy_score(current_targets, current_predictions))
            performance_metrics["f1_score"] = float(f1_score(current_targets, current_predictions, average='weighted'))
        
        # Save metrics
        metrics_path = self.output_dir / f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_path, "w") as f:
            json.dump(performance_metrics, f, indent=2)
        
        return performance_metrics
    
    def check_drift_threshold(self, threshold: float = 0.5) -> bool:
        """
        Check if drift exceeds threshold.
        
        Args:
            threshold: Drift share threshold (0-1)
            
        Returns:
            True if drift exceeds threshold
        """
        if not self.drift_history:
            return False
        
        latest_drift = self.drift_history[-1]
        return latest_drift.get("drift_share", 0) > threshold
    
    def get_drift_summary(self) -> Dict[str, Any]:
        """Get summary of drift history."""
        if not self.drift_history:
            return {"status": "No drift data available"}
        
        drift_shares = [d.get("drift_share", 0) for d in self.drift_history]
        
        return {
            "total_checks": len(self.drift_history),
            "avg_drift_share": np.mean(drift_shares),
            "max_drift_share": np.max(drift_shares),
            "latest_drift_share": drift_shares[-1],
            "drift_detected_count": sum(d.get("dataset_drift", False) for d in self.drift_history)
        }
    
    def alert_on_drift(self, drift_metrics: Dict[str, Any]) -> Optional[str]:
        """
        Generate alert message if significant drift detected.
        
        Args:
            drift_metrics: Drift metrics from report
            
        Returns:
            Alert message or None
        """
        if drift_metrics.get("dataset_drift", False):
            n_drifted = drift_metrics.get("n_drifted_features", 0)
            drift_share = drift_metrics.get("drift_share", 0)
            drifted_features = drift_metrics.get("drifted_features", [])
            
            alert = f"""
            ⚠️  DATA DRIFT DETECTED ⚠️
            
            Timestamp: {drift_metrics.get('timestamp')}
            Drift Share: {drift_share:.2%}
            Drifted Features: {n_drifted}
            Features: {', '.join(drifted_features[:5])}{'...' if len(drifted_features) > 5 else ''}
            
            Action Required: Consider retraining the model with recent data.
            """
            
            return alert.strip()
        
        return None


def create_sample_monitoring_workflow():
    """
    Example workflow for model monitoring.
    """
    from sklearn.datasets import load_wine
    
    # Load reference data (training data)
    wine = load_wine()
    reference_df = pd.DataFrame(wine.data, columns=wine.feature_names)
    reference_df['target'] = wine.target
    
    # Initialize monitor
    monitor = ModelMonitor(reference_df)
    
    # Simulate current data (with slight drift)
    current_df = reference_df.sample(50, random_state=42).copy()
    # Add drift by modifying some values
    current_df['alcohol'] = current_df['alcohol'] * 1.1
    current_df['proline'] = current_df['proline'] * 0.9
    
    # Generate drift report
    print("Generating data drift report...")
    drift_metrics = monitor.generate_data_drift_report(current_df)
    
    print("\nDrift Metrics:")
    print(f"  Dataset Drift: {drift_metrics['dataset_drift']}")
    print(f"  Drift Share: {drift_metrics['drift_share']:.2%}")
    print(f"  Drifted Features: {drift_metrics['drifted_features']}")
    
    # Check for alerts
    alert = monitor.alert_on_drift(drift_metrics)
    if alert:
        print(alert)
    
    # Generate performance report (with mock predictions)
    current_predictions = np.random.randint(0, 3, size=len(current_df))
    current_targets = current_df['target'].values
    
    print("\nGenerating model performance report...")
    perf_metrics = monitor.generate_model_performance_report(
        current_df.drop('target', axis=1),
        current_predictions,
        current_targets
    )
    
    print("\nPerformance Metrics:")
    if perf_metrics.get('has_ground_truth'):
        print(f"  Accuracy: {perf_metrics.get('accuracy', 0):.4f}")
        print(f"  F1 Score: {perf_metrics.get('f1_score', 0):.4f}")
    
    # Get drift summary
    summary = monitor.get_drift_summary()
    print("\nDrift Summary:")
    print(f"  Total Checks: {summary['total_checks']}")
    print(f"  Average Drift Share: {summary['avg_drift_share']:.2%}")
    print(f"  Max Drift Share: {summary['max_drift_share']:.2%}")


if __name__ == "__main__":
    create_sample_monitoring_workflow()
