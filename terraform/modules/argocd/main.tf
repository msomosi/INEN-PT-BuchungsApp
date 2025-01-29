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


resource "kubernetes_manifest" "postgres_application" {
  manifest = {
    apiVersion = "argoproj.io/v1alpha1"
    kind       = "Application"
    metadata = {
      name      = "postgres"
      namespace = "argocd"
    }
    spec = {
      project = "default"
      source = {
        repoURL        = var.repo_url
        targetRevision = var.target_revision
        path          = "terraform/modules/argocd_apps/files"
      }
      destination = {
        server    = "https://kubernetes.default.svc"
        namespace = "default"
      }
      syncPolicy = {
        automated = {
          prune    = true
          selfHeal = true
        }
      }
    }
  }
}