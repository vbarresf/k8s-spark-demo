# Create new storage bucket in the us-west1
# location with Standard Storage

resource "google_storage_bucket" "static" {
 name          = "sdg-demo-train"
 location      = "us-west1"
 storage_class = "STANDARD"

 uniform_bucket_level_access = true
}
