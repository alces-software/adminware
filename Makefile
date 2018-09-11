
.PHONY: unit-test functional-test test setup development-setup rsync \
	watch-rsync remote-run remote-add-dependency ipython

REMOTE_DIR='/tmp/adminware'

unit-test:
	. venv/bin/activate && pytest src/ --ignore=src/nagios_interface/venv

test: unit-test

setup:
	bin/setup

development-setup: setup
	bin/development-setup

rsync:
	rsync --rsh='sshpass -p ${PASSWORD} ssh -l root' -r --copy-links --perms . ${IP}:${REMOTE_DIR}

watch-rsync:
	rerun \
		--name 'Flight Appliance CLI' \
		--pattern '**/*' \
		--exit \
		--no-notify \
		make rsync IP=${IP}

# Note: need to become root to run ipa commands; -t option allows coloured
# output.
remote-run: rsync
	ssh -t root@${IP} "sudo su - -c \"cd ${REMOTE_DIR} && ${COMMAND}\""

remote-add-dependency:
	make remote-run IP=${IP} COMMAND='. venv/bin/activate && pip install ${DEPENDENCY} && pip freeze > requirements.txt'
	scp root@${IP}:${REMOTE_DIR}/requirements.txt requirements.txt

ipython:
	. venv/bin/activate && ipython
