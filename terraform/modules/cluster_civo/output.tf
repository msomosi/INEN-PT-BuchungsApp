output "api_endpoint" {
  value = civo_kubernetes_cluster.cluster.api_endpoint
}

output "cluster" {
  value     = civo_kubernetes_cluster.cluster
  sensitive = true
}

output "cluster_connection" {
  value = format(
    "export KUBECONFIG=%s; kubectl cluster-info; kubectl get pods -A",
    local_sensitive_file.kubeconfig.filename,
  )
}

output "dns_entry" {
  value = civo_kubernetes_cluster.cluster.dns_entry
}

output "domain_name" {
  value = "${civo_kubernetes_cluster.cluster.name}.${var.domain_name}"
}

output "kubeconfig" {
  value = local_sensitive_file.kubeconfig.filename
}

output "kubernetes_name" {
  value = civo_kubernetes_cluster.cluster.name
}

output "load_balancer" {
  value = civo_kubernetes_cluster.cluster
}

output "master_ip" {
  value = civo_kubernetes_cluster.cluster.master_ip
}
