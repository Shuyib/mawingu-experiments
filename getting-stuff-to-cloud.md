Use the steps highlighted here

* You'll need a digital ocean account prior. Make one!
* [docker-development-YT-series](https://github.com/Shuyib/docker-development-youtube-series/blob/master/kubernetes/cloud/digitalocean/getting-started.md)
* Follow the example until the create our cluster section and continue edit.

# Create a cluster
It takes some time for it to start up. Hold up!🤚

```bash
doctl kubernetes cluster create ml-zoomcamp-examples --version 1.22.8-do.0 --count 1 --size s-1vcpu-2gb --region lon1
``` 

# Get the kubeconfig for the cluster

```bash
doctl kubernetes cluster kubeconfig save ml-zoomcamp-examples

# you need the config so
cp ~/.kube/config .
```

# Get kubectl
```bash
curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
chmod +x ./kubectl
mv ./kubectl /usr/local/bin/kubectl

# go back to your working directory for the project in your PC
cd ../..

# go back to digital ocean and download the config file: place it the working directory
```

# move your image to digital ocean container registry
```bash
doctl registry login 

# follow instructions specified here https://cloud.digitalocean.com/registry?i=f2095c
```

# build and run images 
```bash
# build for the trained model
docker build -t ping:v001 . 

# run the file 
docker run -it --rm -p 9696:9696 ping:v001  

# test in another terminal
curl localhost:9696/ping
```

# tag image and push
You'll need to use the API Token route. While Authenticating with the registry
```bash
docker tag <my-image> registry.digitalocean.com/<my-registry>/<my-image>
docker push registry.digitalocean.com/<my-registry>/<my-image>  
```
# Getting back to kubectl  
```bash
# confirm if cluster is up
kubectl get nodes

# what about the pods: They'll be some running definitely and they are required 
kubectl get pods -A  
```
# Preparation  
Get a deployments.yaml file that is generic. You can make this from visual studio code or from the documentation. Make
sure you do the following:
1. ensure that the **app**, **name** & ****is consistent e.g ping-deployment and the image has been tagged the right way. The trick is that 
you should use the registry.digitalocean.com/<my-registry>/<my-image>
2. Save the file and call it something like deploymnent.yaml
3. Run. You may need to create a namespace to handle organisation better.  

```bash
kubectl create -f deployments.yaml
```
If you have issues it maybe that the container has been given authorization to run in your cluster. Head to the console
and fix that with   
Making sure that your cluster and the container registry are in the same region

```bash
kubectl describe nameofpod
kubectl delete deploy ping-deployment
```

```bash
kubectl get pods -w
```
# Expose the app to the internet
Make a service. See example

```bash
kubectl apply -f service.yaml
```
