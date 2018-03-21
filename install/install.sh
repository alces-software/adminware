#!/bin/bash
src_dir="${alces_SRC_DIR:-$(mktemp -d /tmp/adminware.XXX)}"
src_url="${alces_SRC_URL:-https://github.com/alces-software/adminware}"
ins_dir="${alces_INS_DIR:-/opt/adminware}"
ins_opt="${alces_INS:-install}"

deps="libyaml ruby bundler"

install_adminware() {
  yum -y install git zlib-devel openssl-devel readline-devel libffi-devel 
  mkdir -p $src_dir $ins_dir
  cd $src_dir
  git clone $src_url $src_dir
  
  source "${src_dir}/install/ui.functions.sh"

  title "Installing necessary files"
  cp -R $src_dir/* $ins_dir/.
  say_done $?

  for dep in ${deps}; do
    source "${ins_dir}/install/${dep}.sh"
    if ! detect_${dep}; then
      fetch_${dep}
    fi
  done

  for dep in ${deps}; do
    if ! detect_${dep}; then
      install_${dep}
    fi
  done

  title "Installing profile hooks"
  doing 'Install'
  cp "${ins_dir}/install/alces-adminware.sh" /etc/profile.d
  say_done $?

  cd $ins_dir/opt/ruby/bin
  ./bundle install --path="vendor"
}

uninstall_adminware() {
  echo "Uninstalling Adminware..."
  rm -rf $ins_dir
  rm -rf /tmp/build
  rm -rf /etc/profile.d/alces-adminware.sh
}

reinstall_adminware() {
  uninstall_adminware
  install_adminware
}

case $ins_opt in
  'install')
    install_adminware
    ;;
  'uninstall')
    uninstall_adminware
    ;;
  'reinstall')
    reinstall_adminware
    ;;
  *)
    echo "'$ins_opt' - Unknown option. Available options are 'install', 'uninstall' or 'reinstall'"
    exit 1
    ;;
esac
