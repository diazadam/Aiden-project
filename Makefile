PY?=python3.11
VENV=.venv311
RUN=$(VENV)/bin/python

setup:
	@if ! command -v $(PY) >/dev/null; then echo "Install Python 3.11 first (brew install python@3.11)"; exit 1; fi
	@test -d $(VENV) || $(PY) -m venv $(VENV)
	$(RUN) -m pip install -U pip
	$(RUN) -m pip install -r requirements.txt

doctor:
	$(RUN) doctor.py

run-chat:
	cd apps/terminal && ../../$(RUN) aiden_pro.py --chat

run-voice:
	cd apps/terminal && ../../$(RUN) aiden_pro.py --voice

run-super:
	cd apps/terminal && ../../$(RUN) aiden_superintelligence.py

run-menubar:
	cd apps/menubar && ../../$(RUN) aiden_menubar.py

run-ctl:
	cd apps/replit-mvp && ../../$(RUN) -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Phase 2: Skills System Targets
skills-test:
	cd apps/replit-mvp && ../../$(RUN) -m pytest -q

connectors-smoke:
	cd apps/replit-mvp && ../../$(RUN) -c "from connectors.openai_llm import OpenAIChat; llm=OpenAIChat(); print(llm.complete('Say pong succinctly').data)"

sandbox-reset:
	rm -rf /tmp/aiden_work || true

doctor:
	$(RUN) -c "import os; req=['OPENAI_API_KEY','AIDEN_MASTER_PIN']; missing=[k for k in req if not os.environ.get(k)]; print('Missing:',missing if missing else 'OK')"

host-list:
	$(RUN) apps/host/host.py list

clean:
	rm -rf $(VENV) __pycache__ *.pyc