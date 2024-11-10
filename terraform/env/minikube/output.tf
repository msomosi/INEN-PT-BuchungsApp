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
