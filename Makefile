SOURCE_LIB:="baurimicrogui/"
MAINPY:="main.py"
COMPILER_SCRIPT:="compiler.sh"
COMPILED_DIR:="dist/baurimicrogui"
PORT:="/dev/ttyACM0"

all: sync reset

install_typings:
	pip install -U micropython-esp32-stubs --target typings --no-user

black:
	black --line-length 89 *.py
	black --line-length 80 baurimicrogui/

uplib:
	ampy put baurimicrogui

rs:
	rshell --port $(PORT)

reset:
	mpremote a0 reset

sync_lib:
	rshell --port /dev/ttyACM0 rsync --mirror $(SOURCE_LIB) /pyboard/$(SOURCE_LIB)

sync_main:
	rshell --port /dev/ttyACM0 cp $(MAINPY) /pyboard/


sync: sync_lib sync_main

run:
	mpremote a0 run $(MAINPY)

srun: sync run

clean:
	rm -rf dist/

compile:
	sh $(COMPILER_SCRIPT)


