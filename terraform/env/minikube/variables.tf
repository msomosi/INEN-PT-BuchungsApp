variable "argocd_namespace" {
  type      = string
  sensitive = false
  default   = "argocd"
}

variable "cluster_name" {
  type      = string
  sensitive = false
  default   = "mcce-dev"
}

variable "domain_name" {
  type    = string
  default = "mathiasrangger.at"
}
