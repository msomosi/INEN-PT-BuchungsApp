resource "kubernetes_secret" "cluster_wildcard" {
  metadata {
    name = "cluster-wildcard-tls"
    namespace = "cert-manager" # Namespace accessible to all applications
  }

  data = {
    "tls.crt" = filebase64("${path.module}/public.pem")
    "tls.key" = filebase64("${path.module}/private.pem")
  }

  type = "kubernetes.io/tls"
}