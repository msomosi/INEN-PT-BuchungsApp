resource "kubernetes_manifest" "booking_app_certificate" {
  manifest = {
    apiVersion = "cert-manager.io/v1"
    kind       = "Certificate"
    metadata = {
      name      = "booking-app-tls"
      namespace = "booking-app-main"
    }
    spec = {
      secretName = "booking-app-tls-secret"
      issuerRef = {
        name = "letsencrypt-prod"
        kind = "ClusterIssuer"
      }
      dnsNames = ["${var.namespace}.${var.cluster_name}.${var.domain_name}"]
    }
  }
}
