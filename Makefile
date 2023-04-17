.PHONY: requirements check-venv

check-venv:
	@test -n "$(VIRTUAL_ENV)" && \
	echo "Using virtual environment: $(VIRTUAL_ENV)" || \
	(echo "Virtual environment is not activated"; exit 1)

pip-tools: check-venv
	pip install --upgrade pip pip-tools wheel

requirements: check-venv
	pip-compile --generate-hashes --resolver backtracking -o requirements/prod.txt pyproject.toml
	pip-compile --extra dev --generate-hashes --resolver backtracking -o requirements/dev.txt pyproject.toml

sync: check-venv
	pip-sync requirements/dev.txt requirements/prod.txt

update-dependencies: requirements sync