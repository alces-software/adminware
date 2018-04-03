cat << EOF > /opt/adminware/lib/firstrun/bin/firstrun
#!/bin/bash
function fr {
  source /etc/profile.d/alces-adminware.sh
  echo "Running Adminware Firstrun Scripts"
  admin job-run --firstrun
  rm -f /opt/adminware/lib/firstrun/RUN
}
trap fr EXIT
EOF

cat << EOF > /opt/adminware/lib/firstrun/bin/firstrun-stop
#!/bin/bash
/bin/systemctl disable adminware-firstrun.service
if [ -f /adminware-firstrun.reboot ]; then
  echo -n "Reboot flag set.. Rebooting.."
  rm -f /adminware-firstrun.reboot
  shutdown -r now
fi
EOF

cat << EOF > /etc/systemd/system/adminware-firstrun.service
[Unit]
Description=FirstRun service
After=network-online.target remote-fs.target
Before=display-manager.service getting@tty1.service
[Service]
ExecStart=/bin/bash /opt/adminware/lib/firstrun/bin/firstrun
Type=oneshot
ExecStartPost=/bin/bash /opt/adminware/lib/firstrun/bin/firstrun-stop
TimeoutSec=0
RemainAfterExit=yes
Environment=HOME=/root
Environment=USER=root
[Install]
WantedBy=multi-user.target
EOF

chmod 664 /etc/systemd/system/adminware-firstrun.service
systemctl daemon-reload
systemctl enable adminware-firstrun.service
touch /opt/adminware/lib/firstrun/RUN
