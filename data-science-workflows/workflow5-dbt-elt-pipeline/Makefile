install:
	# Install dependencies
	pip --no-cache-dir install --upgrade pip &&\
		pip --no-cache-dir install -r requirements.txt

setup:
	# Generate sample data and load into DuckDB
	python scripts/generate_sample_data.py
	python scripts/load_sample_data.py

dbt-run:
	# Run all dbt models
	cd dbt_project && dbt run

dbt-test:
	# Run all dbt tests
	cd dbt_project && dbt test

dbt-docs:
	# Generate and serve dbt documentation
	cd dbt_project && dbt docs generate && dbt docs serve

dagster:
	# Start Dagster UI
	dagster dev -f orchestrator/dagster_pipeline.py

format:
	# Format code
	black scripts/*.py orchestrator/*.py

lint:
	# Lint Python code
	pylint --disable=R,C scripts/*.py orchestrator/*.py

build:
	# Build Docker container
	docker build -t workflow5-dbt-elt .

run:
	# Run Docker container
	docker run -p 3000:3000 workflow5-dbt-elt

push:
	# Push to Docker registry
	# Set REGISTRY environment variable first: export REGISTRY=registry.digitalocean.com/<my-registry>
	docker tag workflow5-dbt-elt ${REGISTRY}/workflow5-dbt-elt:v1
	docker push ${REGISTRY}/workflow5-dbt-elt:v1

deploy:
	# Deploy to Kubernetes
	kubectl apply -f deployments.yaml

clean:
	# Clean generated files
	rm -rf dbt_project/target dbt_project/dbt_packages dbt_project/logs
	rm -rf data/*.duckdb data/*.duckdb.wal

all: install setup dbt-run dbt-test
