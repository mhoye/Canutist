$dashboard_command = "nubis-cron ${project_name}-dashboard /var/www/${project_name}/dashboard.py > /var/www/${project_name}/dashboard.html 2> /var/log/bzdashboard-cron.log"
$bztriage_command = "nubis-cron ${project_name}-bztriage /var/www/${project_name}/bz-triage.py > /var/log/bztriage-cron.log 2>&1"
$bznag_command = "nubis-cron ${project_name}-bznag /var/www/${project_name}/bznag.py > /var/log/bznag-cron.log 2>&1"

# Run it once on boot
cron { "${project_name}-dashboard-onboot"
  command => $dashboard_command,
  user    => $apache::params::user,
  special => 'reboot',
}

# Then every hour
cron::hourly { "${project_name}-dashboard":
  user    => $apache::params::user,
  command => $dashboard_command,
}

file { '/var/log/bzdashboard-cron.log':
  ensure  => 'present',
  owner   => $apache::params::user,
  group   => $apache::params::group,
  require => [
    Class['nubis_apache'],
  ],
}

# 3am job
cron::daily { "${project_name}-bztriage":
  hour    => '3',
  user    => $apache::params::user,
  command => $bztriage_command,
}

file { '/var/log/bztriage-cron.log':
  ensure  => 'present',
  owner   => $apache::params::user,
  group   => $apache::params::group,
  require => [
    Class['nubis_apache'],
  ],
}

# 4am job
cron::daily { "${project_name}-bznag":
  hour    => '4',
  user    => $apache::params::user,
  command => $bznag_command,
}

file { '/var/log/bznag-cron.log':
  ensure  => 'present',
  owner   => $apache::params::user,
  group   => $apache::params::group,
  require => [
    Class['nubis_apache'],
  ],
}
