#!/bin/bash
src_dir="${alces_SRC_DIR:-$(mktemp -d /tmp/adminware.XXX)}"
src_url="${alces_SRC_URL:-https://github.com/alces-software/adminware}"
ins_dir="${alces_INS_DIR:-/opt/adminware}"
ins_opt="${alces_INS:-install}"
source "${src_dir}/install/ui.functions.sh"

deps="libyaml ruby bundler"

install_adminware() {
  yum -y install git zlib-devel openssl-devel readline-devel libffi-devel 
  mkdir -p $src_dir $ins_dir
  cd $src_dir
  git clone $src_url $src_dir

  title "Installing necessary files"
  dirs_to_copy=("bin/" "etc/" "jobs/" "lib/" "logs" "var/" "Gemfile" "Gemfile.lock")
  for i in "${dirs_to_copy[@]}"
  do
    :
    copy_dir $i $ins_dir/
  done
  say_done $?

  for dep in ${deps}; do
    source "${src_dir}/install/${dep}.sh"
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
  source "${src_dir}/install/base.sh"
  say_done $?

  cd $ins_dir/opt/ruby
  bundle install --path="vendor"
}

copy_dir() {
  cp -R $src_dir/$1 $2
}

uninstall_adminware() {
  echo "Uninstalling Adminware..."
  rm -rf $ins_dir
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
