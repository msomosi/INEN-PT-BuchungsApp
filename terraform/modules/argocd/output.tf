output "argocd" {
  value = helm_release.argocd
}

output "admin_password" {
  value     = local.admin_password
  sensitive = true
}

output "fqdn" {
  value = local.fqdn
}
