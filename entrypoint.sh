#!/bin/bash

set -eu

usermod -aG user "${HOST_DIALOUT_GID}"

exec "$@"
