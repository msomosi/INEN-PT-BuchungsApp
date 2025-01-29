variable "namespace" {
  type        = string
  description = "Namespace for acrgo-cd"
  default     = "argocd"
}

variable "helm_values" {
  default     = {}
  description = "Additional settings which will be passed to the Helm chart values"
}