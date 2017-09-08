cron::hourly { "${project_name}-dashboard":
 user    => 'www-data',
 command => "nubis-cron ${project_name}-dashboard /var/www/${project_name}/dashboard.py > /var/www/${project_name}/dashboard.html",
}
