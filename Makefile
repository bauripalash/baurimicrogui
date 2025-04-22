install_typings:
	pip install -U micropython-esp32-stubs --target typings --no-user

black:
	black --line-length 80 *.py
