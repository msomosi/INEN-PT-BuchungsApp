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

variable "argocd_repository" {
  type    = string
  default = "https://github.com/msomosi/INEN-PT-BuchungsApp.git"
}

variable "argocd_revision" {
  type    = string
  default = "main"
}

variable "argocd_path" {
  type    = string
  default = "k8s/overlays/civo"
}
