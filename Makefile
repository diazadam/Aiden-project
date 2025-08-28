PY?=python3.11
VENV=.venv311
RUN=$(VENV)/bin/python

setup:
	@if ! command -v $(PY) >/dev/null; then echo "Install Python 3.11 first (brew install python@3.11)"; exit 1; fi
	@test -d $(VENV) || $(PY) -m venv $(VENV)
	$(RUN) -m pip install -U pip
	$(RUN) -m pip install -r requirements.txt

doctor:
	bash scripts/doctor.sh

run-chat:
	cd apps/terminal && ../../$(RUN) aiden_pro.py --chat

run-voice:
	cd apps/terminal && ../../$(RUN) aiden_pro.py --voice

clean:
	rm -rf $(VENV) __pycache__ *.pyc