output "argocd" {
  value     = module.argocd.helm
  sensitive = true
}

output "argocd_apps" {
  value     = module.argocd_apps.helm
  sensitive = true
}

output "argocd_fqdn" {
  value = module.argocd.fqdn
}

output "cluster" {
  value     = module.cluster_minikube
  sensitive = true
}

output "cluster_host" {
  value = module.cluster_minikube.cluster_host
}

output "yakd_fqdn" {
  value = kubernetes_ingress_v1.yakd_http.spec[0].rule[0].host
}
