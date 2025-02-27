terraform {
  required_providers {
    minikube = {
      source  = "scott-the-programmer/minikube"
      version = ">= 0.4.2"
    }
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = ">= 1.14.0"
    }
  }
}
