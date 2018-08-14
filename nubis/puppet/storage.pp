include nubis_storage

nubis::storage { $project_name:
  type  => 'efs',
  owner => $apache::params::user,
  group => $apache::params::group,
}

# For backups to S3
package { 'awscli':
  ensure => 'latest'
}

file { "/usr/local/bin/${project_name}-backup":
  ensure => file,
  owner  => root,
  group  => root,
  mode   => '0755',
  source => 'puppet:///nubis/files/backup',
}

cron::daily { "${project_name}-backup":
  command => "consul-do $(nubis-metadata NUBIS_PROJECT)-$(nubis-metadata NUBIS_ENVIRONMENT)-backup $(hostname) && nubis-cron ${project_name}-backup /usr/local/bin/${project_name}-backup /data/${project_name} 2>&1 | logger -t ${project_name}-backup",
  # Pick a time between 0-5 hour
  hour    => fqdn_rand(6),
  # Pick a random minute
  minute  => fqdn_rand(60),
}
