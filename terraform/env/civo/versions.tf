terraform {
  required_providers {
    civo = {
      source = "civo/civo"
    }
    helm = {
      source = "hashicorp/helm"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
    }
    utils = {
      source  = "cloudposse/utils"
      version = ">= 1.26.0"
    }
  }
}
