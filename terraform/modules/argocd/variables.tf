locals {
  admin_password     = var.admin_password != "" ? var.admin_password : random_password.password[0].result
  encrypted_password = bcrypt(local.admin_password)
  fqdn               = var.fqdn != "" ? var.fqdn : "argocd.${var.cluster_name}.${var.domain_name}"
}

variable "admin_password" {
  type        = string
  description = "Default password for admin account"
  default     = ""
}

variable "cluster_name" {
  type = string
}

variable "enable_auth" {
  type        = bool
  description = "Enable login for argocd"
  default     = false
}

variable "domain_name" {
  type = string
}

variable "fqdn" {
  type        = string
  description = "The Fully qualified domain name e.g argocd.example.com"
  default     = ""
}

variable "helm_values" {
  default     = {}
  description = "Additional settings which will be passed to the Helm chart values"
}

variable "namespace" {
  type        = string
  description = "Namespace for acrgo-cd"
  default     = "argocd"
}
variable "repo_url" {
  description = "Git repository URL containing the application manifests"
  type        = string
  default     = "https://github.com/msomosi/INEN-PT-BuchungsApp.git"
}

variable "target_revision" {
  description = "Git branch/tag to use"
  type        = string
  default     = "mse_local_testing"
}