#!/bin/sh

trap 'exit 0' INT TERM

# Start Python script
case "$1" in
	-h|--help)
		python /src/main.py "$@"
		;;
	*)
		while true; do
			python /src/main.py "$@" || exit
			printf 'Waiting for %d seconds...\n' "${BULSAT_WAIT:=300}" && \
				sleep "${BULSAT_WAIT}"
		done
		;;
esac
