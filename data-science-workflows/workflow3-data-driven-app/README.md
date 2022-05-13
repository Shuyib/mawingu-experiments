This is a project that illustrated a scenario that a user may face in practice. In this project, one function is responsible for generating data in a interval while another updates a line plot using the Plotly library.

See **plot_timeseries.py** for more information.  

This is an interesting use case since the data loader is directly specified in the container. Mimicking an already existing pipeline to get data.  

# How to build Docker image  

Make a shared volume first. This will be shared between containers. 

```bash
docker volume create data-app
```

For the generate data script


```bash
docker build -t generate_data:v0 .
```

```bash
docker build -t plot-timeseries-app:v0 .
```

# Reduce the size of the image
You'll need to install the [TAR](https://dockersl.im/) and install it according to the instructions in there.  

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
docker start -ia plotly-timeseries-dashboard
```
