resource "kubernetes_config_map" "postgres_initdb" {
  metadata {
    name      = "postgres-initdb"
    namespace = var.namespace
  }

  data = {
    "init.sql" = file("${path.module}/db_dump.sql")  # Keep SQL file in module directory
  }
}

resource "helm_release" "postgresql" {
  name       = "booking-postgres"
  repository = "oci://registry-1.docker.io/bitnamicharts"
  chart      = "postgresql"
  version    = "16.4.4"
  namespace  = var.namespace

  set {
    name  = "global.postgresql.auth.postgresPassword"
    value = var.postgres_password
  }

  set {
    name  = "primary.persistence.size"
    value = "10Gi"
  }

  set {
    name  = "global.storageClass"
    value = "civo-volume"
  }

  set {
    name  = "primary.initdb.scriptsConfigMap"
    value = kubernetes_config_map.postgres_initdb.metadata[0].name
  }

  set {
    name  = "global.postgresql.auth.database"
    value = "booking_db"
  }
}
# In your PostgreSQL module or root main.tf
resource "helm_release" "pgadmin" {
  name       = "booking"
  repository = "https://helm.runix.net"  # Official pgAdmin Helm chart
  chart      = "pgadmin4"
  namespace  = var.namespace  # mcce-dev

  set {
    name  = "env.email"
    value = "admin@example.com"  # pgAdmin login email
  }

  set {
    name  = "env.password"
    value = "AdminPassword123!"  # Change this!
  }

  set {
    name  = "service.type"
    value = "LoadBalancer"
  }

  # Pre-configure PostgreSQL connection
  set {
    name  = "serverDefinitions.servers.1.Name"
    value = "Booking DB"
  }

  set {
    name  = "serverDefinitions.servers.1.Host"
    value = "booking-postgres-postgresql.mcce-dev.svc.cluster.local"
  }

  set {
    name  = "serverDefinitions.servers.1.Port"
    value = "5432"
  }

  set {
    name  = "serverDefinitions.servers.1.Username"
    value = "postgres"
  }

  set {
    name  = "serverDefinitions.servers.1.Password"
    value = var.postgres_password  # Reference your PostgreSQL password
  }
  depends_on = [helm_release.postgresql]
}