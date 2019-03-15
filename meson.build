project(
  'popout3d',
  version: '1.5.0',
  meson_version: '>= 0.40.0'
)

bindir = get_option('bindir')
datadir = get_option('datadir')
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), 'popout3d')

conf = configuration_data()
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'popout3d.in',
  output: 'popout3d',
  configuration: conf,
  install_dir: bindir
)

data_files = [
  'popout3d_spawn',
  'popout3d_start.png',
  'popout3d_logo.png',
  'popout3d_about.png',
  'popout3d.glade',
  'popout3d.dat'
]

foreach file : data_files
  install_data(file, install_dir: pkgdatadir)
endforeach

install_data(
  'popout3d.desktop',
  install_dir: join_paths(datadir, 'applications')
)

install_data(
  'popout3d.1',
  install_dir: join_paths(datadir, 'man', 'man1')
)

install_data(
  'popout3d_logo.png',
  install_dir: join_paths(datadir, 'icons', 'hicolor', '128x128', 'apps')
)
