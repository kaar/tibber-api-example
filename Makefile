.venv/pyvenv.cfg:
	poetry install

init: .venv/pyvenv.cfg
.PHONY: init

run: init
	poetry run python -m example.main
.PHONY: run

clean:
	rm -rf .venv
.PHONY: clean
