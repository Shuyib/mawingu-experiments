This is project gotten from https://www.youtube.com/watch?v=PUhqw0laR3A all credit goes to the person who made the video and [numpy](https://numpy.org/doc/stable/index.html) too. I think scheduling is uber important.

This gives an alternative to apache airflow which is punk rock in its own right. 

I make an application which keeps track of when a dot product was done, waits for 30s and prints something

# How to build the Docker image
```bash
docker build -t dotproduct:v001 .
```

# How to run the Docker image
```bash
docker run -e -it --rm dotproduct:v001
```

# Push the image to docker registry
```bash
docker tag <my-image> registry.digitalocean.com/<my-registry>/<my-image>
docker push registry.digitalocean.com/<my-registry>/<my-image>  
```

# Create the Kubernetes deployment to run the image in the cluster
This is a shortcut to create the YAML file. VSCodium can help you write this as well.

```bash
# specify the name of the job: A cronjob, name of the job, the image, the schedule, do a check and save the file called deployments.yaml
kubectl create cronjob matmulsched --image=dotproduct --schedule="*/5 * * * *" --dry-run=client -o yaml > deployments.yaml
```
Integrate into kubernetes that is, done the DigitalOcean. Do some edits according to MD file in the main directory in project.

# Check if the pod is up and running
```bash
kubectl get nodes -A
kubectl get cronjobs

# See your deployment go every 5 minutes
kubectl get pods --watch

# See the logs to track your job every 5 minutes
kubectl logs name of the job
```

Expected output:

Starting dot product operation at:  2022-04-10 10:35:10.925554
Doing the operation.....
[[3.13924564 3.13924564]
 [0.93624891 0.93624891]]
Stopping job:  2022-04-10 10:35:40.952996


Starting dot product operation at:  2022-04-10 10:40:01.967905
Doing the operation.....
[[-1.82682298 -1.82682298]
 [ 0.98864072  0.98864072]]
Stopping job:  2022-04-10 10:40:31.999712


So cool!
