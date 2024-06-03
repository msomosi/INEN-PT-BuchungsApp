terraform {
  required_providers {
    exoscale = {
      source  = "exoscale/exoscale"
      version = "0.54.1"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.12.1"
    }
  }
}

provider "helm" {
  kubernetes {
    config_path = "kubeconfig"
  }
}

provider "exoscale" {
  key    = var.exo_key
  secret = var.exo_secret
}