output "postgres_service_name" {
  value = kubernetes_service.postgres.metadata[0].name
}