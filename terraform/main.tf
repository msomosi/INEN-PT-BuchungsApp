locals {
  zone = "at-vie-2"
}

resource "exoscale_security_group" "my_security_group" {
  name = "my-sks-cluster-sg"
}

resource "exoscale_security_group_rule" "kubelet" {
  security_group_id = exoscale_security_group.my_security_group.id
  description       = "Kubelet"
  type              = "INGRESS"
  protocol          = "TCP"
  start_port        = 10250
  end_port          = 10250
  # (beetwen worker nodes only)
  user_security_group_id = exoscale_security_group.my_security_group.id
}

resource "exoscale_security_group_rule" "allow_all_ingress" {
  security_group_id = exoscale_security_group.my_security_group.id
  description       = "Allow all ingress"
  type              = "INGRESS"
  protocol          = "TCP"
  start_port        = 1
  end_port          = 65535
  cidr              = "0.0.0.0/0"
}

resource "exoscale_security_group_rule" "allow_all_egress" {
  security_group_id = exoscale_security_group.my_security_group.id
  description       = "Allow all egress"
  type              = "EGRESS"
  protocol          = "TCP"
  start_port        = 1
  end_port          = 65535
  cidr              = "0.0.0.0/0"
}


resource "exoscale_sks_cluster" "my_sks_cluster" {
  zone          = local.zone
  name          = "my-sks-cluster"
  cni           = "cilium"
  service_level = "starter" //Einschalten bei der Übung ansonsten standartmäßig Pro -Version (kostet mehr)
}

resource "exoscale_sks_nodepool" "my_sks_nodepool" {
  zone          = local.zone
  cluster_id    = exoscale_sks_cluster.my_sks_cluster.id
  name          = "my-sks-nodepool"
  instance_type = "standard.medium"
  size          = 3
  security_group_ids = [
    exoscale_security_group.my_security_group.id,
  ]
}

resource "exoscale_sks_kubeconfig" "my_sks_kubeconfig" {
  zone                  = local.zone
  cluster_id            = exoscale_sks_cluster.my_sks_cluster.id
  user                  = "kubernetes-admin"
  groups                = ["system:masters"]
  ttl_seconds           = 3600
  early_renewal_seconds = 300
}
resource "local_sensitive_file" "my_sks_kubeconfig_file" {
  filename        = "kubeconfig"
  content         = exoscale_sks_kubeconfig.my_sks_kubeconfig.kubeconfig
  file_permission = "0600"
}