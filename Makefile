.PHONY: all client clean fclean exe

all: client

client:
	~/scripts/pyinst.sh client.py
	mv dist/client client

clean:
	rm -rf build dist __pycache__ client.spec

fclean: clean
	rm client

exe:
	~/scripts/py_exe.sh -d client.py client.exe
