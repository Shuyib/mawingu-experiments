This is a project that has various examples of how you can use kubernetes to run containers in a docker registry in a cloud provider. The examples are mostly pitched on data science and machine learning however, some don't meet that categorization.  

.
├── data-science-workflows - data science related projects with data loaders, plots, Application programming Interfaces.   
│   ├── README.md - Explanation of the different use cases an data driven application (dataloader + plotter) & an API.  
│   ├── workflow3-data-driven-app  
│   │   ├── dataloader  
│   │   │   ├── deployments.yaml  
│   │   │   ├── Dockerfile  
│   │   │   ├── main.py  
│   │   │   ├── Makefile  
│   │   │   ├── mylib  
│   │   │   │   ├── dataloader.py  
│   │   │   │   └── __init__.py  
│   │   │   ├── Pipfile  
│   │   │   ├── Pipfile.lock  
│   │   │   └── test_main.py  
│   │   ├── README.md  
│   │   └── timeseries_plot  
│   │       ├── deployments.yaml  
│   │       ├── Dockerfile  
│   │       ├── Makefile  
│   │       ├── mylib  
│   │       │   ├── dataloader.py  
│   │       │   ├── __init__.py    
│   │       ├── Pipfile  
│   │       ├── Pipfile.lock  
│   │       └── plot_timeseries.py  
│   └── workflow4-data-science-api  
│       ├── app.py   
│       ├── deployments.yml  
│       ├── Dockerfile  
│       ├── iris-fit-k-nearest-neighbors-pickle-model.ipynb  
│       ├── iris_knn_model.pkl  
│       ├── Makefile  
│       ├── pycaret+gradio.zip  
│       ├── README.md   
│       ├── requirements.txt  
│       ├── service.yaml  
│       └── test_api_endpoint.ipynb  
├── getting-stuff-to-cloud.md - a summary of how its done of digital ocean.  
├── kubernetes-scheduling - example where you run a cronjob every 5 minutes: Here a job that does a dot product on multidimensional arrays made with numpy.  
│   ├── deployments.yaml - manifest file that specifies instructions that will be given to the kubernetes cluster. It is a cron job meaning that it will run after a certain interval.  
│   ├── Dockerfile - a file that runs the whole application.  
│   ├── matmulsched.py - Python script that records the timestamp before the dot product is run and wait for a few minutes and stops.  
│   ├── Pipfile - contains the requirements of the project as well as the python version.  
│   ├── Pipfile.lock - Just freezes the requirements for the project.  
│   └── README.md - Summary of what the project is about and how to run it.  
├── LICENSE - CC0-1.0 license   
├── ping-app - a simple flask application that prints out pong if you run a CURL request.    
│   ├── deployments.yaml - manifest file that specifies instructions that will be given to the kubernetes cluster.  
│   ├── Dockerfile - a file that packages and runs the application like a zip file.  
│   ├── ping.py - python file that defines the Flask application and associated methods.  
│   ├── Pipfile - contains the requirements of the project as well as the python version.  
│   ├── Pipfile.lock - Just freezes the requirements for the project.  
│   └── service.yaml - manifest that is passed to the k8s cluster to expose the application to the internet via an IP and host.  
└── README.md - the file you are reading.   

You can make these containers made smaller to run more with your limited capacity on digital ocean. Will explore that in the future. Enjoy!  

