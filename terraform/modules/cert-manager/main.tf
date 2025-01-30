resource "helm_release" "cert_manager" {
  name       = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"
  namespace  = "cert-manager"
  version    = "v1.14.4" # Update to latest version

  create_namespace = true

  set {
    name  = "installCRDs"
    value = "true"
  }
}

