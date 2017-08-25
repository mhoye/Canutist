#Install directories, etc for triagebot

file { '/var/local/bz-triage':
  ensure => directory,
  owner  => lighttpd,
  group  => lighttpd,
  mode   => '0755',
}
