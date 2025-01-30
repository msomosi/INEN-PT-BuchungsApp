resource "kubernetes_manifest" "cluster_issuer" {
  manifest = {
    apiVersion = "cert-manager.io/v1"
    kind       = "ClusterIssuer"
    metadata = {
      name = "letsencrypt-prod"
    }
    spec = {
      acme = {
        email  = "matzi789@gmx.at"
        server = "https://acme-v02.api.letsencrypt.org/directory"
        privateKeySecretRef = {
          name = "letsencrypt-prod"
        }
        solvers = [{
          http01 = {
            gatewayHTTPRoute = {
              parentRefs = [{
                name      = "booking-app-gateway"
                namespace = "booking-app-main"
                kind      = "Gateway"
              }]
            }
          }
        }]
      }
    }
  }
}