data "utils_deep_merge_yaml" "argocd_values" {
  input = [
    file("${path.module}/files/argocd-apps.yaml"),
    var.helm_values
  ]
}

resource "helm_release" "argocd_apps" {
  provider = helm

  name            = "argocd-apps"
  repository      = "https://argoproj.github.io/argo-helm"
  chart           = "argocd-apps"
  cleanup_on_fail = true

  namespace        = var.namespace
  create_namespace = true

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