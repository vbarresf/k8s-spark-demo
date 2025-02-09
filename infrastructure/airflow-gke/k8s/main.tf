variable "project_id" {
  type = string
}

variable "region" {
  default = "us-central1"
}

variable "zone" {
  default = "us-central1-f"
}

variable "cluster_name" {
  default = "airflow-cluster"
}

variable "service_account_name" {
  default = "worker"
}

variable "service_account_namespace" {
  default = "default"
}

provider "google" {
  project = var.project_id
  region = var.region
}

data "google_client_config" "provider" {}

data "google_container_cluster" "airflow_cluster" {
  name = var.cluster_name
  location = var.zone
}

output "cluster_ca_certificate" {
  value = data.google_container_cluster.airflow_cluster.master_auth[0].cluster_ca_certificate
}

output "access_token" {
  value = data.google_client_config.provider.access_token
}

output "cluster_endpoint" {
  value =  "https://${data.google_container_cluster.airflow_cluster.endpoint}"
}

provider "kubernetes" {
  load_config_file = false

  host  = "https://${data.google_container_cluster.airflow_cluster.endpoint}"
  token = data.google_client_config.provider.access_token
  cluster_ca_certificate = base64decode(
    data.google_container_cluster.airflow_cluster.master_auth[0].cluster_ca_certificate,
  )
}

resource "google_project_iam_binding" "storage_access" {
  role    = "roles/storage.admin"

  members = [
    "serviceAccount:${var.service_account_name}@${var.project_id}.iam.gserviceaccount.com",
  ]
}

resource "google_project_iam_binding" "publisher" {
  role    = "roles/pubsub.publisher"

  members = [
    "serviceAccount:${var.service_account_name}@${var.project_id}.iam.gserviceaccount.com",
  ]
}

resource "google_project_iam_binding" "cloud_sql" {
  role    = "roles/cloudsql.client"

  members = [
    "serviceAccount:${var.service_account_name}@${var.project_id}.iam.gserviceaccount.com",
  ]
}

module "my-app-workload-identity" {
  source    = "terraform-google-modules/kubernetes-engine/google//modules/workload-identity"
  name      = var.service_account_name
  namespace = var.service_account_namespace
  project_id   = var.project_id
}

resource "google_project_service" "sql_admin_api" {
  project = var.project_id
  service = "sqladmin.googleapis.com"
}

resource "google_project_service" "storage" {
  project = var.project_id
  service = "storage-component.googleapis.com"
}

resource "google_project_service" "storage_json" {
  project = var.project_id
  service = "storage-api.googleapis.com"
}