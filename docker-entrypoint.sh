#!/bin/bash
set -e

case "$@" in
*)
    exec gunicorn --config gunicorn_config.py "app:create_app()"
    ;;
esac
