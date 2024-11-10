module "cluster_minikube" {
  source = "../../modules/cluster_minikube"

  cluster_name = var.cluster_name
  domain_name  = var.domain_name
}

data "netparse_url" "cluster_ip" {
  url = module.cluster_minikube.cluster_host
}

module "argocd" {
  source = "../../modules/argocd"

  domain_name  = "${data.netparse_url.cluster_ip.host}.nip.io"
  cluster_name = var.cluster_name
  namespace    = var.argocd_namespace

  depends_on = [module.cluster_minikube]
}

data "utils_deep_merge_yaml" "argocd_apps" {
  input = [
    file("files/argocd-booking-app.yaml"),
    file("files/argocd-envoy.yaml"),
  ]
}

module "argocd_apps" {
  source = "../../modules/argocd_apps"

  namespace   = var.argocd_namespace
  helm_values = data.utils_deep_merge_yaml.argocd_apps.output

  depends_on = [module.argocd]
}
