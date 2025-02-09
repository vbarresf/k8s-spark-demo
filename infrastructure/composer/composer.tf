provider "google-beta" {
  project = "sdg-demo"
  region  = "us-central1"
}

resource "google_project_service" "composer_api" {
  provider = google-beta
  project = "sdg-demo"
  service = "composer.googleapis.com"
  // Disabling Cloud Composer API might irreversibly break all other
  // environments in your project.
  disable_on_destroy = false
  // this flag is introduced in 5.39.0 version of Terraform. If set to true it will
  //prevent you from disabling composer_api through Terraform if any environment was
  //there in the last 30 days
  check_if_service_has_usage_on_destroy = true
}

resource "google_service_account" "custom_service_account" {
  provider = google-beta
  account_id   = "sdg-composer-service-account"
  display_name = "Service Account for sdg-demo Composer"
}

resource "google_project_iam_member" "custom_service_account" {
  provider = google-beta
  project  = "sdg-demo"
  member   = format("serviceAccount:%s", google_service_account.custom_service_account.email)
  // Role for Public IP environments
  role     = "roles/composer.worker"
}

resource "google_composer_environment" "example_environment" {
  provider = google-beta
  name = "sdg-demo-composer"

  config {

    software_config {
      image_version = "composer-1.20.12-airflow-1.10.15"
    }

    node_config {
      service_account = google_service_account.custom_service_account.email
    }

  }
}