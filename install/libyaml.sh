detect_libyaml() {
  [ -f "/opt/adminware/opt/lib/lib/libyaml.so" ]
}

fetch_libyaml() {
  title "Fetching LibYAML"
  curl -L http://pyyaml.org/download/libyaml/yaml-0.1.5.tar.gz > /tmp/yaml-source.tar.gz 
}

install_libyaml() {
  title "Intalling LibYAML"
  mkdir /tmp/build
  tar -C /tmp/build -xzf /tmp/yaml-source.tar.gz
  
  cd /tmp/build/yaml*

  ./configure --prefix="/opt/adminware/opt/lib"
  make
  make install
}
