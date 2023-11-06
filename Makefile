.PHONY: clean

build:
	python -m flit build

install:
	python -m flit build && python -m flit install

clean:
	rm -rf .pytest_cache .dist


