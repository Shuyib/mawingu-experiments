This is a project that has various examples of how you can use kubernetes to run containers in a docker registry in a cloud provider. The examples are mostly pitched on data science and machine learning however, some don't meet that categorization.  

.
├── getting-stuff-to-cloud.md - a summary of how its done of digital ocean.  
├── kubernetes-scheduling - example where you run a cronjob every minutes: Here a job that does a dot product on multidimensional arrays made with numpy.  
│   ├── deployments.yaml  
│   ├── Dockerfile  
│   ├── matmulsched.py  
│   ├── Pipfile  
│   ├── Pipfile.lock  
│   └── README.md  
├── ping-app - a simple flask application that prints out pong if you run a CURL request.  
│   ├── deployments.yaml  
│   ├── Dockerfile  
│   ├── ping.py  
│   ├── Pipfile  
│   ├── Pipfile.lock  
│   └── service.yaml  
└── README.md - the file you are reading.  

You can make these containers made smaller to run more with your limited capacity on digital ocean. Will explore that in the future. Enjoy!  

