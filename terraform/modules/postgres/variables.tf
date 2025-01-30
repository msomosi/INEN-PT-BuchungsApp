variable "namespace" {
  type    = string
  default = "mcce-dev"
}

variable "postgres_password" {
  type      = string
  sensitive = true
  default   = "password123"
}