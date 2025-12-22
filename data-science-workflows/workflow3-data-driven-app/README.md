This is a project that illustrated a scenario that a user may face in practice. In this project, one function is responsible for generating data in a interval while another updates a line plot using the matplotlib library.

See **plot_timeseries.py** for more information.  

This is an interesting use case since the data loader is directly specified in the container. Mimicking an already existing pipeline to get data.  

The data loader is responsible for generating data and uploading it to an object storage. The data is then used by the time series plotter to plot the data. It might help to have an aggregation script that runs maybe every midnight to have a single file to load the data. Additionally, you can use a database for example PostgreSQL (Plus since you can make vector databases) or MySQL to improve the application load times.

## Workflow Architecture

The timeseries plot application now uses SQLite for data persistence with incremental loading optimization:

```mermaid
flowchart LR
    A[S3 Object Storage] -->|Download CSV| B[load_s3_to_database]
    B -->|Check Existing Data| C[(SQLite Database)]
    B -->|Compare Records| J[Duplicate Detection]
    J -->|Insert Only New| C
    B -->|Delete CSV| D[Cleanup]
    C -->|Query| E[query_timeseries_data]
    E -->|DataFrame| F[plot_data_from_dataframe]
    F -->|Generate PNG| G[lineplot.png]
    G -->|Upload| H[S3 Object Storage]
    G -->|Delete PNG| I[Cleanup]
    
    style C fill:#90EE90
    style A fill:#87CEEB
    style H fill:#87CEEB
    style D fill:#FFB6C1
    style I fill:#FFB6C1
    style J fill:#FFD700
```

**Key Benefits:**
- **Data Persistence**: Historical data accumulates in SQLite across runs
- **Incremental Loading**: Only new data is inserted, preventing duplicates and speeding up large datasets
- **Reduced S3 Calls**: Local database caching minimizes API requests
- **Query Flexibility**: Easy to add filters, aggregations, and time windows
- **Scalable**: Simple migration path to PostgreSQL or TimescaleDB

**Performance Optimization:**

The `load_s3_to_database` function now performs intelligent duplicate detection:
- Compares incoming data against existing records (x,y pairs)
- Only inserts new data points not already in the database
- Logs statistics: `Inserted N new records (skipped M duplicates)`
- Significantly faster for large datasets with overlapping data

# Setup your digital ocean spaces 

```bash
# export your environment variables
# or add them to your .bashrc or .bash_profile
export digi_ocean_api_key=your_digital_ocean_api_key
export ENDPOINT_URL=https://ams3.digitaloceanspaces.com
export SECRET_KEY=your_secret_key
export SPACES_ID=your_spaces_id
export SPACES_NAME=your_spaces_name
```

# Running the Data Loader locally

```bash
# create a virtual environment
pipenv install

# activate the virtual environment
pipenv shell

# Update packages
pipenv update

# security vurnerabilities
pipenv check

# update lock file
pipenv lock

# run the data loader
python generate_data.py
```

# Seeing the data as its being generated

```python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Function to read the CSV file and return a DataFrame
def read_csv():
    return pd.read_csv('data.csv')

# Function to update the plot
def update_plot(frame):
    """load data and update plot"""
    data = read_csv()
    plt.cla()
    plt.plot(data['x'], data['y']) 
    plt.xlabel('X')
    plt.ylabel('Y')  
    plt.title('Real-time Data Plot')

# Set up the plot
fig, ax = plt.subplots()

# Call the update_plot function every second
ani = animation.FuncAnimation(fig, update_plot, interval=1000)  # Update every second

# Show the plot
plt.show()
```


# How to build Docker image  

For the generate data script


```bash
docker build -t generate_data:v0 .
```

```bash
docker build -t plot-timeseries-app:v0 .
```

# Reduce the size of the image (Optional/Not tested)
Docker slim is a tool that can be used to reduce the size of the image.  
Learn more about it [here](https://hub.docker.com/r/dslim/docker-slim)

```bash
docker pull dslim/docker-slim:latest
```

```bash
#generate data
docker-slim build --http-probe generate_data:v0
```

```bash
#plot timeseries
docker-slim build --http-probe plot-timeseries-app:v0
```


# How to run the Docker container

Specify shared named docker volume. To store the data somewhere and the other container will have access to it.  

```bash
docker run -e ENDPOINT_URL -e SECRET_KEY -e SPACES_ID -e SPACES_NAME generate_data:v0
```

See if data is being populated in the directory  

```bash
docker exec nameofcontainer tail data/data.csv
```

```bash
docker run -e ENDPOINT_URL -e SECRET_KEY -e SPACES_ID -e SPACES_NAME plot-timeseries-app:v0
```

# Restart Container

```bash
docker start -ia plot-timeseries-app:v0
```

# Expected Output from running docker image or K8s logs name of the pod  

**Dataloader**  
Uploaded data to object storage True  
Checking great data expectations for project  
Uploaded data expectations to object storage True  

**Time series plot**  
loaded data into working directory for now  
made plot saved it in directory for now  
Uploaded data to object storage True  
