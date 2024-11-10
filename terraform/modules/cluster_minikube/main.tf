resource "minikube_cluster" "docker" {
  driver       = "docker"
  cluster_name = var.cluster_name

  addons = concat([
    "dashboard",
    "default-storageclass",
    "ingress",
    "ingress-dns",
    "metrics-server",
    "storage-provisioner",
  ], var.addons)
}

resource "local_sensitive_file" "kubeconfig" {
  content = templatefile("${path.module}/templates/kubeconfig-template.tftpl", {
    client_certificate     = base64encode(minikube_cluster.docker.client_certificate)
    client_key             = base64encode(minikube_cluster.docker.client_key)
    cluster_host           = minikube_cluster.docker.host,
    cluster_ca_certificate = base64encode(minikube_cluster.docker.cluster_ca_certificate)
    cluster_name           = minikube_cluster.docker.cluster_name
  })
  filename        = "kubeconfig"
  file_permission = "0600"

}
