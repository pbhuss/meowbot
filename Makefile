.PHONY: server install update_venv

server:
	supervisord -c instance/supervisord.conf

install: instance update_venv
	@echo
	@echo "To finish installation, edit the configuration files in ./instance/"

instance:
	cp -r instance_example/ instance/

venv:
	virtualenv -p python3 venv

update_venv: venv
	venv/bin/pip install -r requirements.txt --upgrade
