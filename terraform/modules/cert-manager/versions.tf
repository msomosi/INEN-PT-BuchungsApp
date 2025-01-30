terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.16.1"
    }
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = ">= 1.14.0"
    }
  }
}
