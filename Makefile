.PHONY: help b c t tidy reqsFr reqsInst
.DEFAULT_GOAL := help

FILES=`find . -type f -name "*.py"`

help:
	@echo ""
	@echo "Pyphlogiston commands:"
	@echo ""
	@echo "target   | description"
	@echo "---------+------------"
	@echo "b          fix style with black"
	@echo "c          check typing with mypy"
	@echo "t          run tests quickly with the default Python"
	@echo "tidy       fix style, type check, and test"
	@echo "reqsFr     freeze requirements.txt in etc"
	@echo "reqsInst   install requirements.txt in etc"
	@echo ""
b:
	@PYTHONPATH=$(DPATH) black --config etc/pyproject.toml $(FILES)
c:
	@PYTHONPATH=$(DPATH) mypy --config-file etc/mypy.ini $(FILES)
t:
	@PYTHONPATH=$(DPATH) python -m pytest -c etc/pytest.ini tests --capture=no
tidy: b c t
	echo "tidy"
install:
	@python setup.py install
reqsFr:
	@pip freeze > etc/requirements.txt
reqsInst:
	@pip install -r etc/requirements.txt
