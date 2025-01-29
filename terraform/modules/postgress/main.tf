resource "kubernetes_persistent_volume_claim" "postgres_pvc" {
  metadata {
    name = "postgres-pvc"
  }
  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = "10Gi"
      }
    }
    storage_class_name = "civo-volume"
  }
}

resource "kubernetes_config_map" "postgres_config" {
  metadata {
    name = "postgres-config"
  }
  data = {
    POSTGRES_DB   = "citizix_db"
    POSTGRES_USER = "citizix_user"
  }
}

resource "kubernetes_secret" "postgres_secret" {
  metadata {
    name = "postgres-secret"
  }
  data = {
    POSTGRES_PASSWORD = base64encode("S3cret")
  }
  type = "Opaque"
}

resource "kubernetes_config_map" "postgres_init" {
  metadata {
    name = "postgres-init-sql"
  }
  data = {
    "init.sql" = file("${path.module}/init.sql") # Path to your SQL dump
  }
}

resource "kubernetes_stateful_set" "postgres" {
  metadata {
    name = "postgres"
  }
  spec {
    service_name = "postgres"
    replicas     = 1
    selector {
      match_labels = {
        app = "postgres"
      }
    }
    template {
      metadata {
        labels = {
          app = "postgres"
        }
      }
      spec {
        init_container {
          name    = "init-db"
          image   = "postgres:14"
          command = ["sh", "-c", "cp /docker-entrypoint-initdb.d/* /init-scripts/"]
          volume_mount {
            name       = "init-scripts"
            mount_path = "/init-scripts"
          }
          volume_mount {
            name       = "sql-dump"
            mount_path = "/docker-entrypoint-initdb.d"
          }
        }
        container {
          name  = "postgres"
          image = "postgis/postgis:14-3.3"
          env_from {
            config_map_ref {
              name = kubernetes_config_map.postgres_config.metadata[0].name
            }
          }
          env_from {
            secret_ref {
              name = kubernetes_secret.postgres_secret.metadata[0].name
            }
          }
          port {
            container_port = 5432
          }
          volume_mount {
            name       = "postgres-storage"
            mount_path = "/var/lib/postgresql/data"
          }
          volume_mount {
            name       = "init-scripts"
            mount_path = "/docker-entrypoint-initdb.d"
          }
        }
        volume {
          name = "init-scripts"
          empty_dir {}
        }
        volume {
          name = "sql-dump"
          config_map {
            name = kubernetes_config_map.postgres_init.metadata[0].name
          }
        }
      }
    }
    volume_claim_template {
      metadata {
        name = "postgres-storage"
      }
      spec {
        access_modes = ["ReadWriteOnce"]
        resources {
          requests = {
            storage = "10Gi"
          }
        }
        storage_class_name = "civo-volume"
      }
    }
  }
}

resource "kubernetes_service" "postgres" {
  metadata {
    name = "postgres"
  }
  spec {
    selector = {
      app = "postgres"
    }
    port {
      port = 5432
    }
  }
}