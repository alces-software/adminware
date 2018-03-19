detect_ruby() {
  [ -d "/opt/adminware/opt/ruby" ]
}

fetch_ruby() {
  title "Fetching Ruby"
  curl https://cache.ruby-lang.org/pub/ruby/2.4.1.tar.gz ruby-source.tar.gz
}

install_ruby() {
  title "Installing Ruby"
  tar -C home/tmp/build -xzf home/tmp/src/ruby-source.tar.gz
  cd home/tmp/build/ruby-*
  ./configure --prefix"$ins_dir/opt/ruby" --enable-shared -disable-install-doc
  make
  make install
}
