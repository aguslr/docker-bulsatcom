#!/bin/sh

# Start Python script
case "$1" in
	-h|--help)
		python /usr/local/bin/bsc.py "$@"
		;;
	*)
		while true; do
			python /usr/local/bin/bsc.py "$@" || exit
			printf 'Waiting for %d seconds...\n' "${BULSAT_WAIT:=300}" && \
				sleep "${BULSAT_WAIT}"
		done
		;;
esac
