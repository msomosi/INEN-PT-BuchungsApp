resource "kubernetes_namespace" "cnpg" {
  metadata {
    name = "cnpg-system"
  }
}

resource "kubernetes_manifest" "cnpg_operator" {
  manifest = yamldecode(file("${path.module}/cloudnativepg.yaml"))
}
