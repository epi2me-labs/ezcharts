.PHONY: develop docs

PYTHON ?= python3

IN_VENV=. ./venv/bin/activate
PROJECT=ezcharts

venv/bin/activate:
	test -d venv || $(PYTHON) -m venv venv
	${IN_VENV} && pip install pip --upgrade
	${IN_VENV} && pip install -r requirements.txt

develop: venv/bin/activate
	${IN_VENV} && python setup.py develop

test: venv/bin/activate
	${IN_VENV} && pip install 'flake8<6.0.0' flake8-rst-docstrings flake8-docstrings flake8-import-order flake8-forbid-visual-indent
	${IN_VENV} && flake8 ${PROJECT} \
		--import-order-style google --application-import-names ${PROJECT} \
		--statistics --max-line-length 88
	# demo should run without error
	${IN_VENV} && python setup.py install
	${IN_VENV} && ${PROJECT} demo

IN_BUILD=. ./pypi_build/bin/activate
pypi_build/bin/activate:
	test -d pypi_build || $(PYTHON) -m venv pypi_build --prompt "(pypi) "
	${IN_BUILD} && pip install pip --upgrade
	${IN_BUILD} && pip install --upgrade pip setuptools twine wheel readme_renderer[md] keyrings.alt

.PHONY: sdist
sdist: pypi_build/bin/activate
	${IN_BUILD} && python setup.py sdist

.PHONY: clean
clean:
	rm -rf __pycache__ dist build venv ${PROJECT}.egg-info tmp docs/_build
