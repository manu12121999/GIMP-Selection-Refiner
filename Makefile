cat:
	cat Makefile

pip:
	bash ./setup.sh

clean_pip:
	rm -fr ./gimpenv
	rm -f ./sam2.1_hiera_base_plus.pt

uv:
	bash ./setup_uv.sh

clean_uv:
	rm -fr ./.git ./.venv
	rm -f ./gimpenv
	rm -f ./.gitignore
	rm -f ./.python-version
	rm -f ./README.md
	rm -f ./main.py
	rm -f ./pyproject.toml
	rm -f ./sam2.1_hiera_base_plus.pt
	rm -f ./uv.lock
