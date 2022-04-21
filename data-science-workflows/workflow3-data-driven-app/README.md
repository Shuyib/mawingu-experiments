This is a project that illustrated a scenario that a user may face in practice. In this project, one function is responsible for generating data in a interval while another updates a line plot using the Plotly library.

See **plot_timeseries.py** for more information.  

This is an interesting use case since the data loader is directly specified in the container. Mimicking an already existing pipeline to get data.  

# How to build Docker image

For the generate data script


```bash
docker build -t generate_data:v0 -f Dockerfile_generatedata .
```

```bash
docker build -t workflow3-data-science-app:v0 .
```

# Reduce the size of the image
You'll need to install the [TAR](https://dockersl.im/) and install it  

```bash
#todo
```


# How to run the Docker container

Specify shared named docker volume. To store the data somewhere and the other container will have access to it.  

```bash
ocker volume create storage
```

```bash
docker run -p 8050:8050 -v $(PWD):app/data --name plotly-timeseries-dashboard
```


# Restart Container

```bash
docker start -ia plotly-timeseries-dashboard
```
