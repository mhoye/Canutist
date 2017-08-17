variable "account" {
  default = ""
}

variable "region" {
  default = "us-west-2"
}

variable "environment" {
  default = "stage"
}

variable "wait_for_capacity_timeout" {
  default = "10m"
}

variable "service_name" {
  default = "planet"
}

variable "ami" {}
