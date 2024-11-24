# INEN-PT-BuchungsApp
 Die "Buchungs- und Reservierungsplattform für ein Studentenwohnheim" stellt eine innovative Lösung im Bereich der digitalen Buchungssysteme dar, die sich nahtlos in den Alltag einer Fachhochschule integriert.

## Verfügbar in Kubernetes
https://mcce-apeni.mathiasrangger.at/home

## Build images
./bin/build_local.sh


## Run app in docker-compose

### Install docker
https://docs.docker.com/engine/install/ubuntu/

### Start app
./bin/run_local.sh



## Run app in minikube
### Install minikube
https://gist.github.com/wholroyd/748e09ca0b78897750791172b2abb051

### Install terraform

https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli

### Install kubectl

https://kubernetes.io/docs/tasks/tools/


### Start app
cd terraform/env/minikube\
terraform init\
terraform plan\
terraform apply -auto-approve
