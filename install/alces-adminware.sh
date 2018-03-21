if [ "$UID" == "0" ]; then
  if [ -d /opt/adminware/install/base.sh ]; then
    if [ -r /opt/adminware/install/base.sh ]; then
      if [ "${-#*/opt/adminware/install/base.sh}" != "$-" ]; then
        . /opt/adminware/install/base.sh
      else
        . /opt/adminware/install/base.sh 2>&1
      fi
    fi
  fi
fi
