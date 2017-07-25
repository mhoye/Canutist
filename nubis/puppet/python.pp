class { 'python':
  version => 'system',
  pip     => true,
  dev     => true,
}

package { 'git':
  ensure => 'present',
}

python::pip { 'bztools':
  ensure  => 'present',
  url     => 'git+https://github.com/LegNeato/bztools.git@27f7fc1ae28de9de52d0c85120ba67a9a881db92',
  require => [
    Package['git'],
  ]
}

python::pip { 'remoteobjects':
  ensure => '1.2.1',
}

python::pip { 'validate-email':
  ensure => '1.3',
}

python::pip { 'lockfile':
  ensure => '0.12.2',
}

python::pip { 'bleach':
  ensure => '2.0.0',
}

python::pip { 'python-dateutil':
  ensure => '2.6.1',
}

python::pip { 'six':
  ensure => '1.10.0',
}