if id |grep -qw siteadmin ; then
  admin(){
    sudo /opt/adminware/adminware.rb
  }
fi
