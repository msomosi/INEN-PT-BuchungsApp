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
