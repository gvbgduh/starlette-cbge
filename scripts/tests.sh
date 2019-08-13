#!/usr/bin/env bash

pytest
black ../ --check
mypy ../ --ignore-missing-imports --disallow-untyped-def
