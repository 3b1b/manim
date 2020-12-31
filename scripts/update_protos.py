#!/usr/bin/env python
"""
This is intended to be run from manim/grpc
"""

import os

CMD_STRING = """
poetry run python \
    -m grpc_tools.protoc \
    -I./proto \
    --python_out=./gen \
    --grpc_python_out=./gen \
        ./proto/frameserver.proto \
        ./proto/renderserver.proto
"""
os.system(CMD_STRING)
