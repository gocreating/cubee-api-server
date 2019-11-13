#!/bin/sh

# REBUILD=1 ./run_tests.sh to rebuild the docker images
if [ -n "$REBUILD" ]; then
    docker-compose --file docker-compose-run-tests.yaml build
fi

docker-compose --file docker-compose-run-tests.yaml up --exit-code-from api-server-test-runner
