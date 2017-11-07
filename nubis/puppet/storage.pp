include nubis_storage

nubis::storage { $project_name:
  type  => 'efs',
  owner => $apache::params::user,
  group => $apache::params::group,
}
