variable "namespace" {
  type = string
  description = "Kubernetes namespace for PostgreSQL"
  default = "default"  # Or your preferred default namespace
}

variable "sql_dump_path" {
  type = string
  description = "Path to SQL dump file"
  default = "init.sql"
}