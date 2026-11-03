.PHONY: check check-core check-harbor check-run-isolation

check: check-core check-harbor

check-core:
	uv run --locked --group gateway python script/check.py

check-harbor:
	uv run --isolated --locked --python 3.12 --group harbor python script/check.py --harbor-only

check-run-isolation:
	uv run --locked --group gateway python script/check-run-isolation.py --ipv6
