detect_ruby() {
  [ -d "/opt/adminware/opt/ruby" ]
}

fetch_ruby() {
  title "Fetching Ruby"
  curl -L https://cache.ruby-lang.org/pub/ruby/2.4.1.tar.gz > /tmp/ruby-source.tar.gz
}

install_ruby() {
  title "Installing Ruby"
  tar -C /tmp/build -xzf /tmp/ruby-source.tar.gz
  cd /tmp/build/ruby-*
  ./configure --prefix"$ins_dir/opt/ruby" --enable-shared -disable-install-doc \
    --with-libyaml --with-opt-dir="/opt/adminware/opt/lib"
  make
  make install
}
