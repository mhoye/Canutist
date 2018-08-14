fluentd::configfile { $project_name: }

fluentd::source { 'bznag-output':
  configfile  => $project_name,
  type        => 'tail',
  format      => '/^(?<time>[^\]]*) - (?<level>[^\]]*) - (?<message>.*)?$/',
  time_format => '%Y-%M-%d %H:%M:%S %Z',

  tag         => "forward.${project_name}.bznag.stdout",
  config      => {
    'read_from_head' => true,
    'path'           => '/var/log/bznag.log',
    'pos_file'       => '/var/log/bznag.pos',
  },
}

fluentd::source { 'bztriage-output':
  configfile  => $project_name,
  type        => 'tail',
  format      => '/^(?<time>[^\]]*) - (?<level>[^\]]*) - (?<message>.*)?$/',
  time_format => '%Y-%M-%d %H:%M:%S %Z',

  tag         => "forward.${project_name}.bztriage.stdout",
  config      => {
    'read_from_head' => true,
    'path'           => '/var/log/bz-triage.log',
    'pos_file'       => '/var/log/bz-triage.pos',
  },
}

fluentd::source { 'bzsignup-output':
  configfile  => $project_name,
  type        => 'tail',
  format      => '/^(?<time>[^\]]*) - (?<level>[^\]]*) - (?<message>.*)?$/',
  time_format => '%Y-%M-%d %H:%M:%S %Z',

  tag         => "forward.${project_name}.bzsignup.stdout",
  config      => {
    'read_from_head' => true,
    'path'           => '/var/log/bz-signup.log',
    'pos_file'       => '/var/log/bz-signup.pos',
  },
}

fluentd::source { 'bzdashboard-cron':
  configfile => $project_name,
  type       => 'tail',
  format     => 'none',

  tag        => "forward.${project_name}.bzdashboard.stdout",
  config     => {
    'read_from_head' => true,
    'path'           => '/var/log/bzdashboard-cron.log',
    'pos_file'       => '/var/log/bzdashboard-cron.pos',
  },
}

fluentd::source { 'bztriage-cron':
  configfile => $project_name,
  type       => 'tail',
  format     => 'none',

  tag        => "forward.${project_name}.bztriage.cron",
  config     => {
    'read_from_head' => true,
    'path'           => '/var/log/bztriage-cron.log',
    'pos_file'       => '/var/log/bztriage-cron.pos',
  },
}

fluentd::source { 'bznag-cron':
  configfile => $project_name,
  type       => 'tail',
  format     => 'none',

  tag        => "forward.${project_name}.bznag.cron",
  config     => {
    'read_from_head' => true,
    'path'           => '/var/log/bznag-cron.log',
    'pos_file'       => '/var/log/bznag-cron.pos',
  },
}

