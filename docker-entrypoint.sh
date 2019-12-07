#!/bin/bash
set -e

case "$@" in
*)
    exec gunicorn --config gunicorn_config.py "app.main:create_app()"
    ;;
esac
