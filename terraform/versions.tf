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

provider "aws" {
  region                  = "us-east-1"  # Exoscale nutzt die S3 API, die mit dem AWS Provider kompatibel ist.
  access_key              = var.exo_key
  secret_key              = var.exo_secret
  skip_credentials_validation = true
  skip_metadata_api_check = true
  s3_force_path_style     = true
  endpoints {
    s3 = "https://sos-${local.zone}.exo.io"
  }
}