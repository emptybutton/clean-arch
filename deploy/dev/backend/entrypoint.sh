#!/bin/bash

uv sync
source ${UV_PROJECT_ENVIRONMENT}/bin/activate
alembic upgrade head
$@
