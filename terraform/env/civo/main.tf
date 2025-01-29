module "cluster_civo" {
  source = "../../modules/cluster_civo"

  cluster_name = var.cluster_name
  domain_name  = var.domain_name
}

module "argocd" {
  source = "../../modules/argocd"

  cluster_name = var.cluster_name
  domain_name  = var.domain_name
  namespace    = var.argocd_namespace
  enable_auth  = true

  depends_on = [module.cluster_civo]
}

data "utils_deep_merge_yaml" "argocd_apps" {
  input = concat([
    for namespace in var.namespaces : templatefile("templates/argocd-app-booking-app.yaml", {
      repository = var.argocd_application.repository,
      revision   = namespace,
      path       = "${var.argocd_application.path}-${namespace}",
      namespace  = replace(namespace, "/[^a-zA-Z0-9-\\.]/", "-")
    })],
    [file("files/argocd-app-envoy.yaml")]
  )

  depends_on = [module.argocd]
}

module "argocd_apps" {
  source = "../../modules/argocd_apps"

  namespace   = var.argocd_namespace
  helm_values = data.utils_deep_merge_yaml.argocd_apps.output

  depends_on = [module.argocd, data.utils_deep_merge_yaml.argocd_apps]
}

resource "kubernetes_manifest" "envoy-config" {
  manifest = {
    apiVersion = "gateway.envoyproxy.io/v1alpha1"
    kind       = "EnvoyProxy"
    metadata = {
      name      = "custom-proxy-config"
      namespace = "envoy-gateway-system"
    }

    spec = {
      mergeGateways = true
    }
  }

  depends_on = [module.argocd_apps]
}

resource "kubernetes_manifest" "envoy_gatewayclass" {
  manifest = yamldecode(file("files/envoy-civo-merged-gwc.yaml"))

  depends_on = [module.argocd_apps]
}

resource "kubernetes_manifest" "argocd_gateway" {
  manifest = yamldecode(templatefile("templates/argocd-gateway.yaml", {
    cluster_name = var.cluster_name,
    domain_name  = var.domain_name,
  }))

  depends_on = [module.argocd_apps]
}

resource "kubernetes_manifest" "argocd_http_route" {
  manifest = yamldecode(file("files/argocd-http-route.yaml"))

  depends_on = [module.argocd_apps]
}

data "kubernetes_resources" "envoy" {
  api_version    = "v1"
  kind           = "Service"
  namespace      = "envoy-gateway-system"
  label_selector = "app.kubernetes.io/component=proxy"

  depends_on = [module.argocd_apps]
}

data "civo_loadbalancer" "envoy" {
  id = data.kubernetes_resources.envoy.objects[0].metadata.annotations["kubernetes.civo.com/loadbalancer-id"]

  depends_on = [data.kubernetes_resources.envoy]
}

resource "kubernetes_manifest" "app_gateway" {
  for_each = var.namespaces
  manifest = yamldecode(templatefile("templates/gateway-booking-app.yaml", {
    namespace    = replace(each.value, "/[^a-zA-Z0-9-\\.]/", "-")
    cluster_name = var.cluster_name,
    domain_name  = var.domain_name,
  }))

  depends_on = [module.argocd_apps]
}

module "postgres" {
  source = "../../modules/postgres"

  depends_on = [module.cluster_civo]
}
