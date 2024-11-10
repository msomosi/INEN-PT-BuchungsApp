provider "kubernetes" {
  host = module.cluster_minikube.cluster_host

  client_certificate     = module.cluster_minikube.client_certificate
  client_key             = module.cluster_minikube.client_key
  cluster_ca_certificate = module.cluster_minikube.cluster_ca_certificate
}


provider "helm" {
  kubernetes {
    host = module.cluster_minikube.cluster_host

    client_certificate     = module.cluster_minikube.client_certificate
    client_key             = module.cluster_minikube.client_key
    cluster_ca_certificate = module.cluster_minikube.cluster_ca_certificate
  }
}
