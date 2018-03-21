detect_ruby() {
  [ -d "/opt/adminware/opt/ruby" ]
}

fetch_ruby() {
  title "Fetching Ruby"
  curl -L https://cache.ruby-lang.org/pub/ruby/2.5/ruby-2.5.0.tar.gz > /tmp/ruby-source.tar.gz
}

install_ruby() {
  title "Installing Ruby"
  
  doing 'Extract'
  tar -C /tmp/build -xzf /tmp/ruby-source.tar.gz
  say_done $?

  cd /tmp/build/ruby-*

  doing 'Configure'
  ./configure --prefix="${ins_dir}/opt/ruby" --enable-shared -disable-install-doc \
    --with-libyaml --with-opt-dir="/opt/adminware/opt/lib" \
    &> /tmp/logs/ruby-configure.log
  say_done $?

  doing 'Compile'
  make &> /tmp/logs/ruby-compile.log
  say_done $?

  doing 'Install'
  make install &> /tmp/logs/ruby-install.log
  say_done $?
}
