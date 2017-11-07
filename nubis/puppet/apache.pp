# Define how Apache should be installed and configured
# We should try to recycle the puppetlabs-apache puppet module in the future:
# https://github.com/puppetlabs/puppetlabs-apache

# Define how Apache should be installed and configured

class { 'nubis_apache':
}

file { '/var/log/bz-signup.log':
  ensure  => 'present',
  owner   => $apache::params::user,
  group   => $apache::params::group,
  require => [
    Class['nubis_apache'],
  ],
}

file { "/var/www/${project_name}/dashboard.html":
  ensure  => 'present',
  owner   => $apache::params::user,
  group   => $apache::params::group,
  require => [
    Class['nubis_apache'],
  ],
}

file { '/var/local/bz-triage':
  ensure => 'link',
  target => "/data/${project_name}",
}

file { '/var/log/bz-triage.log':
  ensure  => 'present',
  owner   => $apache::params::user,
  group   => $apache::params::group,
  require => [
    Class['nubis_apache'],
  ],
}

file { '/var/log/bznag.log':
  ensure  => 'present',
  owner   => $apache::params::user,
  group   => $apache::params::group,
  require => [
    Class['nubis_apache'],
  ],
}

class { 'apache::mod::cgid': }

apache::vhost { $project_name:
    port               => 80,
    default_vhost      => true,
    docroot            => "/var/www/${project_name}",
    docroot_owner      => 'root',
    docroot_group      => 'root',
    block              => ['scm'],
    setenvif           => [
      'X-Forwarded-Proto https HTTPS=on',
      'Remote_Addr 127\.0\.0\.1 internal',
      'Remote_Addr ^10\. internal',
    ],
    access_log_env_var => '!internal',
    access_log_format  => '%a %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\"',

    directories        => [
      {
        path           => "/var/www/${project_name}",
        directoryindex => 'index.py index.html',
        addhandlers    => [
          {
            handler    => 'cgi-script',
            extensions => ['.py']
          }
        ],
        options        => ['+ExecCGI'],
      },
    ],

    custom_fragment    => "
# Clustered without coordination
FileETag None
",
    headers            => [
      "set X-Nubis-Version ${project_version}",
      "set X-Nubis-Project ${project_name}",
      "set X-Nubis-Build   ${packer_build_name}",
    ],
    rewrites           => [
      {
        comment      => 'HTTPS redirect',
        rewrite_cond => ['%{HTTP:X-Forwarded-Proto} =http'],
        rewrite_rule => ['. https://%{HTTP:Host}%{REQUEST_URI} [L,R=permanent]'],
      }
    ]
}

