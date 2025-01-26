provider "helm" {
  kubernetes {
    config_path = "../../kubeconfig-${var.cluster_name}"
  }
}

provider "kubernetes" {
  config_path = "../../kubeconfig-${var.cluster_name}"
}
