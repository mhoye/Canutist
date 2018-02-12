module "worker" {
  source                    = "github.com/nubisproject/nubis-terraform//worker?ref=v2.1.0"
  region                    = "${var.region}"
  environment               = "${var.environment}"
  account                   = "${var.account}"
  service_name              = "${var.service_name}"
  ami                       = "${var.ami}"
  elb                       = "${module.load_balancer.name}"
  nubis_sudo_groups         = "team_webops,nubis_global_admins"
  instance_type             = "${var.instance_type}"
  wait_for_capacity_timeout = "20m"
  health_check_grace_period = "600"
}

module "load_balancer" {
  source               = "github.com/nubisproject/nubis-terraform//load_balancer?ref=v2.1.0"
  region               = "${var.region}"
  environment          = "${var.environment}"
  account              = "${var.account}"
  service_name         = "${var.service_name}"
  ssl_cert_name_prefix = "${var.service_name}"

  health_check_target = "HTTP:80/index.css"
}

module "dns" {
  source       = "github.com/nubisproject/nubis-terraform//dns?ref=v2.1.0"
  region       = "${var.region}"
  environment  = "${var.environment}"
  account      = "${var.account}"
  service_name = "${var.service_name}"
  target       = "${module.load_balancer.address}"
}

module "storage" {
  source                 = "github.com/nubisproject/nubis-terraform//storage?ref=v2.1.0"
  region                 = "${var.region}"
  environment            = "${var.environment}"
  account                = "${var.account}"
  service_name           = "${var.service_name}"
  storage_name           = "${var.service_name}"
  client_security_groups = "${module.worker.security_group}"
}

module "mail" {
  source       = "github.com/nubisproject/nubis-terraform//mail?ref=v2.1.0"
  region       = "${var.region}"
  environment  = "${var.environment}"
  account      = "${var.account}"
  service_name = "${var.service_name}"
}
