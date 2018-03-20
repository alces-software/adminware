detect_libyaml() {
  [ -f "/opt/adminware/opt/lib/lib/libyaml.so" ]
}

fetch_libyaml() {
  title "Fetching LibYAML"
  curl -L http://pyyaml.org/download/libyaml/yaml-0.1.5.tar.gz > /tmp/yaml-source.tar.gz 
}

install_libyaml() {
  title "Intalling LibYAML"

  doing 'Extract'
  mkdir /tmp/build
  tar -C /tmp/build -xzf /tmp/yaml-source.tar.gz
  say_done $?
 
  cd /tmp/build/yaml*
  
  doing 'Configure'
  ./configure --prefix="/opt/adminware/opt/lib"
  say_done $?

  doing 'Compile'
  make
  say_done $?

  doing 'Install'
  make install  
  say_done $?
}
