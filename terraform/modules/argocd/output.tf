output "admin_password" {
  value     = local.admin_password
  sensitive = true
}

output "fqdn" {
  value = local.fqdn
}

output "helm" {
  value = helm_release.argocd
}
