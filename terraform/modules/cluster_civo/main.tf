resource "civo_firewall" "firewall" {
  name = "${var.cluster_name}-firewall"
}

# Cluster name is randomly generated when not specified
resource "civo_kubernetes_cluster" "cluster" {
  name = var.cluster_name
  #kubernetes_version = "1.29.2-k3s1"
  write_kubeconfig = true

  # Default firewall in the default network:
  firewall_id = civo_firewall.firewall.id
  pools {
    size       = "g4s.kube.medium" # "g4s.kube.xsmall", "g4s.kube.small", "g4s.kube.medium"
    node_count = 3
  }
}

resource "local_sensitive_file" "kubeconfig" {
  content         = civo_kubernetes_cluster.cluster.kubeconfig
  filename        = "${path.module}/../../kubeconfig-${civo_kubernetes_cluster.cluster.name}"
  file_permission = "0600"
}
