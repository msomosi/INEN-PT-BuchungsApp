resource "random_password" "password" {
  count            = length(var.admin_password) == 0 ? 1 : 0
  length           = 16
  special          = true
  override_special = "_%@"
}

data "utils_deep_merge_yaml" "argocd_values" {
  input = [
    file("${path.module}/files/argocd.yaml"),
    yamlencode(var.helm_values)
  ]
}

resource "helm_release" "argocd" {
  provider = helm

  name            = "argocd"
  repository      = "https://argoproj.github.io/argo-helm"
  chart           = "argo-cd"
  cleanup_on_fail = true

  namespace        = var.namespace
  create_namespace = true

  set {
    name  = "global.domain"
    value = local.fqdn
  }

  set {
    name  = "configs.params.server\\.disable\\.auth"
    value = !var.enable_auth
  }

  set {
    name  = "configs.params.server\\.insecure"
    value = "true"
  }

  set {
    name  = "configs.secret.argocdServerAdminPassword"
    value = local.encrypted_password
  }

  values = [data.utils_deep_merge_yaml.argocd_values.output]
}