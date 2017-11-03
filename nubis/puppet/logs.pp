fluentd::configfile { $project_name: }

fluentd::source { 'bznag-output':
  configfile  => $project_name,
  type        => 'tail',
  format      => '/^(?<time>[^\]]*) - (?<level>[^\]]*) - (?<message>.*)?$/',
  time_format => '%Y-%M-%d %H:%M:%S %Z',

  tag         => 'forward.bznag.node.stdout',
  config      => {
    'read_from_head' => true,
    'path'           => "/var/log/${project_name}/bznag.log",
    'pos_file'       => "/var/log/${project_name}/bznag.pos",
  },
}


fluentd::source { 'bztriage-output':
  configfile  => $project_name,
  type        => 'tail',
  format      => '/^(?<time>[^\]]*) - (?<level>[^\]]*) - (?<message>.*)?$/',
  time_format => '%Y-%M-%d %H:%M:%S %Z',

  tag         => 'forward.bztriage.node.stdout',
  config      => {
    'read_from_head' => true,
    'path'           => "/var/log/${project_name}/bz-triage.log",
    'pos_file'       => "/var/log/${project_name}/bz-triage.pos",
  },
}


fluentd::source { 'bzsignup-output':
  configfile  => $project_name,
  type        => 'tail',
  format      => '/^(?<time>[^\]]*) - (?<level>[^\]]*) - (?<message>.*)?$/',
  time_format => '%Y-%M-%d %H:%M:%S %Z',

  tag         => 'forward.bzsignup.node.stdout',
  config      => {
    'read_from_head' => true,
    'path'           => "/var/log/${project_name}/bz-signup.log",
    'pos_file'       => "/var/log/${project_name}/bz-signup.pos",
  },
}
