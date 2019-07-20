#!/bin/bash
set -e

case "$@" in
*)
    exec gunicorn --config gunicorn_config.py app.app:app
    ;;
esac
