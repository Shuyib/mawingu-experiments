This is a project that illustrated a scenario that a user may face in practice. In this project, one function is responsible for generating data in a interval while another updates a line plot using the matplotlib library.

See **plot_timeseries.py** for more information.  

This is an interesting use case since the data loader is directly specified in the container. Mimicking an already existing pipeline to get data.  

# How to build Docker image  

For the generate data script


```bash
docker build -t generate_data:v0 .
```

```bash
docker build -t plot-timeseries-app:v0 .
```

# Reduce the size of the image
You'll need to install the [TAR](https://dockersl.im/) and install it  

```bash
#generate data


#workflow3-data-science-app
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
