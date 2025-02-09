variable "project_id" {
  type = string
}

variable "postgres_user" {
  default = "airflow"
}
variable "postgres_pw" {
  default = "airflow"
}

variable "region" {
  default = "us-central1"
}

variable "redis_disk" {
  default = "airflow-redis-disk"
}

variable "zone" {
  default = "us-central1-f"
}

variable "cluster_name" {
  default = "airflow-cluster"
}

variable "db_instance" {
  default = "airflow-db"
}

provider "google" {
  project = var.project_id
  region = var.region
}

provider "google-beta" {
  project = var.project_id
  region = var.region
}

########################################################

resource "google_compute_disk" "airflow-redis-disk" {
  name  = var.redis_disk
  type  = "pd-ssd"
  size = "200"
  zone  = var.zone
}

#########################################################

resource "google_sql_database_instance" "airflow-db" {
  name = var.db_instance
  database_version = "POSTGRES_12"
  region = var.region
  settings {
    tier = "db-g1-small"
  }
}

resource "google_sql_database" "airflow-schema" {
  name = "airflow"
  instance = google_sql_database_instance.airflow-db.name
}

resource "google_sql_user" "proxyuser" {
  name = var.postgres_user
  password = var.postgres_pw
  instance = google_sql_database_instance.airflow-db.name
  host = "cloudsqlproxy~%"
}

#############################################################

resource "google_container_cluster" "airflow-cluster" {
  provider = google-beta
  name = var.cluster_name
  location = var.zone
  initial_node_count = 1

  workload_identity_config {
    identity_namespace = "${var.project_id}.svc.id.goog"
  }

  node_config {
    machine_type = "n1-standard-4"
    workload_metadata_config {
      node_metadata = "GKE_METADATA_SERVER"
    }

    oauth_scopes = ["https://www.googleapis.com/auth/devstorage.read_only"]
  }

  lifecycle {
    prevent_destroy = true
  }
}
