<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | >= 2.16.1 |
| <a name="requirement_kubernetes"></a> [kubernetes](#requirement\_kubernetes) | >= 2.33.0 |
| <a name="requirement_utils"></a> [utils](#requirement\_utils) | >= 1.26.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_helm"></a> [helm](#provider\_helm) | >= 2.16.1 |
| <a name="provider_random"></a> [random](#provider\_random) | n/a |
| <a name="provider_utils"></a> [utils](#provider\_utils) | >= 1.26.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [helm_release.argo-cd](https://registry.terraform.io/providers/hashicorp/helm/latest/docs/resources/release) | resource |
| [random_password.password](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/password) | resource |
| [utils_deep_merge_yaml.argocd_values](https://registry.terraform.io/providers/cloudposse/utils/latest/docs/data-sources/deep_merge_yaml) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_admin_password"></a> [admin\_password](#input\_admin\_password) | Default password for admin account | `string` | `""` | no |
| <a name="input_cluster_name"></a> [cluster\_name](#input\_cluster\_name) | n/a | `string` | n/a | yes |
| <a name="input_domain_name"></a> [domain\_name](#input\_domain\_name) | n/a | `string` | n/a | yes |
| <a name="input_enable_auth"></a> [enable\_auth](#input\_enable\_auth) | Enable login for argocd | `bool` | `false` | no |
| <a name="input_fqdn"></a> [fqdn](#input\_fqdn) | The Fully qualified domain name e.g argocd.example.com | `string` | `""` | no |
| <a name="input_helm_values"></a> [helm\_values](#input\_helm\_values) | Additional settings which will be passed to the Helm chart values | `map` | `{}` | no |
| <a name="input_namespace"></a> [namespace](#input\_namespace) | Namespace for acrgo-cd | `string` | `"argocd"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_admin_password"></a> [admin\_password](#output\_admin\_password) | n/a |
| <a name="output_argo-cd"></a> [argo-cd](#output\_argo-cd) | n/a |
| <a name="output_fqdn"></a> [fqdn](#output\_fqdn) | n/a |
<!-- END_TF_DOCS -->
