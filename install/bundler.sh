detect_bundler() {
  [ -f "/opt/adminware/opt/ruby/bin/bundle" ]
}

fetch_bundler() {
  title "Fetching Bundler"
  curl -L https://rubygems.org/downloads/bundler-1.10.6.gem > /tmp/src/bundler.gem
}

install_bundler() {
  title "Installing Bundler"
  "/opt/adminware/opt/ruby/bin/gem" install bundler
}
