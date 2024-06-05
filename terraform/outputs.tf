# Outputs
output "my_sks_cluster_endpoint" {
  value = exoscale_sks_cluster.my_sks_cluster.endpoint
}
#
output "my_sks_kubeconfig" {
  value = local_sensitive_file.my_sks_kubeconfig_file.filename
}

output "my_sks_connection" {
  value = format(
    "export KUBECONFIG=%s; kubectl cluster-info; kubectl get pods -A",
    local_sensitive_file.my_sks_kubeconfig_file.filename,
  )
}