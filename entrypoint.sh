#!/bin/bash

set -eu

usermod -aG "${HOST_DIALOUT_GID}" user

exec "$@"
