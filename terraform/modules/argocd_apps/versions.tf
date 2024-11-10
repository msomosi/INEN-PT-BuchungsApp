terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.16.1"
    }
    utils = {
      source  = "cloudposse/utils"
      version = ">= 1.26.0"
    }
  }
}
