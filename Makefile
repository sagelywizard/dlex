test:
	python -m unittest discover tests/

typecheck:
	mypy db.py

checkfile:
	@test $(FILE)
	@echo [Running tests...]
	@echo # || true to have `make` shut up on errors
	@python -m unittest tests/test_$(FILE) || true
	@echo
	@echo [Running type checks...]
	@echo
	@mypy $(FILE) || true
	@echo
	@echo [Running pylint...]
	@echo
	@pylint --msg-template='PYLINT: {msg_id}:{line:3d},{column}: {obj}: {msg}' $(FILE) | grep --color=never 'PYLINT' || true
