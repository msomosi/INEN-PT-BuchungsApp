output "api_endpoint" {
  value = ""
}

output "cluster" {
  value     = minikube_cluster.docker
  sensitive = true
}

output "cluster_host" {
  value = minikube_cluster.docker.host
}

output "client_certificate" {
  value = minikube_cluster.docker.client_certificate
}

output "client_key" {
  value = minikube_cluster.docker.client_key
}

output "cluster_ca_certificate" {
  value = minikube_cluster.docker.cluster_ca_certificate
}

output "cluster_name" {
  value = minikube_cluster.docker.cluster_name
}

output "cluster_connection" {
  value = format(
    "export KUBECONFIG=%s; kubectl cluster-info; kubectl get pods -A",
    local_sensitive_file.kubeconfig.filename,
  )
}

output "dns_entry" {
  value = ""
}

output "domain_name" {
  value = "${minikube_cluster.docker.cluster_name}.${var.domain_name}"
}

output "kubeconfig" {
  value = "none"
}

output "kubernetes_name" {
  value = minikube_cluster.docker.cluster_name
}

output "master_ip" {
  value = ""
}
