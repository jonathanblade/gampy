#!/bin/sh

VERSION=1.0.0
DISTPATH=dist
BUILDPATH=_build

echo "__version__ = '${VERSION}'" > ./gampy/__init__.py

poetry run black gampy
poetry run black main.py
poetry run pyinstaller --distpath ${DISTPATH} \
                       --workpath ${BUILDPATH} \
                       --specpath ${BUILDPATH} \
                       --add-data ../3rdparty/GAMP/gamp:. \
                       --add-data ../3rdparty/GAMP/gamp.cfg:. \
                       --add-data ../3rdparty/RNXCMP/crx2rnx:. \
                       --name gampy \
                       --onefile \
                       --clean \
                       main.py

zip -j ./dist/gampy-v${VERSION}-linux64.zip ./dist/gampy README.md gampy.cfg
