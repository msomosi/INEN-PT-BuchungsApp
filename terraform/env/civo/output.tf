output "api_endpoint" {
  value = module.cluster_civo.api_endpoint
}

output "argocd" {
  value     = module.argocd
  sensitive = true
}

output "argocd_admin_passwort" {
  value     = module.argocd.admin_password
  sensitive = true
}

output "argocd_fqdn" {
  value = module.argocd.fqdn
}

output "cluster" {
  value     = module.cluster_civo
  sensitive = true
}

output "cluster_connection" {
  value = module.cluster_civo.cluster_connection
}

output "domain_name" {
  value = module.cluster_civo.domain_name
}
