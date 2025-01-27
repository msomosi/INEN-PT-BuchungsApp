
variable "argocd_application" {
  type = object({
    repository = string
    revision   = string
    path       = string
  })
  default = {
    repository = "localhost"
    revision   = "main"
    path       = "."
  }
}

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
  default = "roomify.stark-industries.at"
}

variable "namespaces" {
  description = "Add this branches as namespaces/subdomains to cluster"
  type        = set(string)
  default     = ["mse_local_testing", "mathias"]
}
