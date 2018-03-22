admin() {
  (cd /opt/adminware && PATH="/opt/adminware/opt/ruby/bin:$PATH" bin/adminware "$@")
}

if [ "$ZSH_VERSION" ]; then 
  export admin
else
  export -f admin
fi
alias adm=admin
alias adminware=admin
