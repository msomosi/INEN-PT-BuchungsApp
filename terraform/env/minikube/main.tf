module "cluster_minikube" {
  source = "../../modules/cluster_minikube"

  cluster_name = var.cluster_name
  domain_name  = var.domain_name

  addons = [
    "metallb",
    "yakd"
  ]
}

data "netparse_url" "cluster_ip" {
  url = module.cluster_minikube.cluster_host
}

module "argocd" {
  source = "../../modules/argocd"

  domain_name  = "${data.netparse_url.cluster_ip.host}.nip.io"
  cluster_name = var.cluster_name
  namespace    = var.argocd_namespace

  depends_on = [module.cluster_minikube]
}

data "utils_deep_merge_yaml" "argocd_apps" {
  input = [
    templatefile("files/argocd-booking-app.yaml", {
      repository = var.argocd_repository,
      revision   = var.argocd_revision,
      path       = var.argocd_path
    }),
    file("files/argocd-envoy.yaml"),
  ]
}

module "argocd_apps" {
  source = "../../modules/argocd_apps"

  namespace   = var.argocd_namespace
  helm_values = data.utils_deep_merge_yaml.argocd_apps.output

  depends_on = [module.argocd]
}

resource "kubernetes_config_map_v1_data" "metallb" {
  metadata {
    name      = "config"
    namespace = "metallb-system"
  }

  force = true
  data = {
    config = templatefile("files/metallb-config.yaml", {
      cidr = cidrsubnet("${data.netparse_url.cluster_ip.host}/24", 1, 1)
    })
  }
}

resource "kubernetes_ingress_v1" "yakd_http" {
  metadata {
    name      = "yakd-http"
    namespace = "yakd-dashboard"
  }

  spec {
    ingress_class_name = "nginx"
    rule {
      host = "yakd.${var.cluster_name}.${data.netparse_url.cluster_ip.host}.nip.io"
      http {
        path {
          path = "/"
          backend {
            service {
              name = "yakd-dashboard"
              port {
                number = "80"
              }
            }
          }
        }
      }
    }
  }
}
