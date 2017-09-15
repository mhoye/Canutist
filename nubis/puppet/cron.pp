cron::hourly { "${project_name}-dashboard":
 user    => 'www-data',
 command => "nubis-cron ${project_name}-dashboard /var/www/${project_name}/dashboard.py > /var/www/${project_name}/dashboard.html",
}

cron::daily { "${project_name}-bztriage":
 hour    => '3',
 user	 => 'www-data',
 command => "nubis-cron ${project_name}-bztriage /var/www/${project_name}/bz-triage.py >/dev/null 2>&1",
}
