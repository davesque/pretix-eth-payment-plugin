#!/bin/bash

set -o nounset
set -o errexit

cd /pretix/src

export DJANGO_SETTINGS_MODULE=docker_settings
export DATA_DIR=/data

WEB_MULTIPLIER="${WEB_MULTIPLIER:-3}"
export WEB_CONCURRENCY="${WEB_CONCURRENCY:-$(($WEB_MULTIPLIER * $(nproc)))}"

if [ ! -d $DATA_DIR/logs ]; then
    mkdir $DATA_DIR/logs;
fi

if [ ! -d $DATA_DIR/media ]; then
    mkdir $DATA_DIR/media;
fi

# Create a pretix.cfg file in the current directory from environment variables.
# This will cause pretix to override certain config settings based on env vars.
./update_cfg_from_env.py \
  --whitelist=pretix_cfg_env_whitelist.txt \
  'PRETIX_' \
  pretix.cfg

if [ "$1" == "webworker" ]; then
    shift
    exec gunicorn pretix.wsgi \
        --name pretix \
        --max-requests 1200 \
        --max-requests-jitter 50 \
        --log-level info \
        --log-file - \
        --bind "0.0.0.0:$PORT" \
        "$@"
fi

if [ "$1" == "taskworker" ]; then
    export C_FORCE_ROOT=True
    exec celery -A pretix.celery_app worker -l info
fi

# Example usages:
# pretix runperiodic (cron job)
# pretix migrate --noinput (database migrations)
# pretix collectstatic --noinput (django static files)
# pretix compress (django compressor offline mode)
# pretix --help (django management help)

exec python3 -m pretix "$@"
