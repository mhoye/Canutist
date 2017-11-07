cron::hourly { "${project_name}-dashboard":
 user    => $apache::params::user,
 command => "nubis-cron ${project_name}-dashboard /var/www/${project_name}/dashboard.py > /var/www/${project_name}/dashboard.html 2> /var/log/bzdashboard-cron.log",
}

file { '/var/log/bzdashboard-cron.log':
  ensure  => 'present',
  owner   => 'www-data',
  group   => 'www-data',
  require => [
    Class['nubis_apache'],
  ],
}

cron::daily { "${project_name}-bztriage":
 hour    => '3',
 user	 => 'www-data',
 command => "nubis-cron ${project_name}-bztriage /var/www/${project_name}/bz-triage.py > /var/log/bztriage-cron.log 2>&1",
}

file { '/var/log/bztriage-cron.log':
  ensure  => 'present',
  owner   => 'www-data',
  group   => 'www-data',
  require => [
    Class['nubis_apache'],
  ],
}

cron::daily { "${project_name}-bznag":
 hour	 => '4',
 user    => 'www-data',
 command => "nubis-cron ${project_name}-bztriage /var/www/${project_name}/bznag.py > /var/log/bznag-cron.log 2>&1",
}

file { '/var/log/bznag-cron.log':
  ensure  => 'present',
  owner   => 'www-data',
  group   => 'www-data',
  require => [
    Class['nubis_apache'],
  ],
}
