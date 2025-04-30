install_typings:
	pip install -U micropython-esp32-stubs --target typings --no-user

black:
	black --line-length 89 *.py
	black --line-length 80 baurimicrogui/

uplib:
	ampy put baurimicrogui

upmain:
	ampy put main.py

rs:
	rshell --port /dev/ttyACM0

sync_lib:
	rshell --port /dev/ttyACM0 rsync --mirror baurimicrogui /pyboard/baurimicrogui

sync_main:
	rshell --port /dev/ttyACM0 cp main.py /pyboard/

sync: sync_lib sync_main

run:
	mpremote a0 run main.py

srun: sync run


