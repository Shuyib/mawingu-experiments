This is a project that has various examples of how you can use kubernetes to run containers in a docker registry in a cloud provider. The examples are mostly pitched on data science and machine learning however, some don't meet that categorization.  

.  
├── getting-stuff-to-cloud.md - a summary of how its done of digital ocean.  
├── kubernetes-scheduling - example where you run a cronjob every 5 minutes: Here a job that does a dot product on multidimensional arrays made with numpy.  
│   ├── deployments.yaml - manifest file that specifies instructions that will be given to the kubernetes cluster. It is a cron job meaning that it will run after a certain interval.  
│   ├── Dockerfile - a file that runs the whole application.
│   ├── matmulsched.py - Python script that does records the timestamp before the dot product is run and wait for a few minutes and stops.
│   ├── Pipfile - contains the requirements of the project as well as the python version.
│   ├── Pipfile.lock - Just freezes the requirements for the project.
│   └── README.md - Summary of what the project is about and how to run it.
├── ping-app - a simple flask application that prints out pong if you run a CURL request.  
│   ├── deployments.yaml - manifest file that specifies instructions that will be given to the kubernetes cluster.
│   ├── Dockerfile - a file that packages and runs the application like a zip file.
│   ├── ping.py  - python file that defines the Flask application and associated methods.
│   ├── Pipfile - contains the requirements of the project as well as the python version.
│   ├── Pipfile.lock - Just freezes the requirements for the project.
│   └── service.yaml - manifest that is passed to the k8s cluster to expose the application to the internet via an IP and host. 
└── README.md - the file you are reading.  

You can make these containers made smaller to run more with your limited capacity on digital ocean. Will explore that in the future. Enjoy!  

