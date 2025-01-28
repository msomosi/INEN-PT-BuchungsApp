variable "namespace" {
  type        = string
  description = "Namespace for acrgo-cd"
  default     = "argocd"
}

variable "helm_values" {
  default     = {}
  description = "Additional settings which will be passed to the Helm chart values"
}

variable "repo_url" {
  description = "Git repository URL containing the application manifests"
  type        = string
  default     = "https://github.com/msomosi/INEN-PT-BuchungsApp.git"
}

variable "target_revision" {
  description = "Git branch/tag to use"
  type        = string
  default     = "main"
}