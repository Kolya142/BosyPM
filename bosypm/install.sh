#!/usr/bin/bash
IPATH=~/.local/bosy/bin/bspm

if [ ! -z $1 ]; then
    IPATH=$1
fi

if [ -z $1 ]; then
    mkdir -p ~/.local/bosy/
    mkdir -p ~/.local/bosy/bin
    mkdir -p ~/.local/bosy/bin/bspm
    echo "#!/usr/bin/env bash" > ~/.local/bin/bspm-env-bspm
    echo "# Default enviroment for bspm" >> ~/.local/bin/bspm-env-bspm
    echo "PATH=$PATH:~/.local/bosy/bin/bspm $SHELL" >> ~/.local/bin/bspm-env-bspm
    chmod +x ~/.local/bin/bspm-env-bspm
    echo "Use \"bspm-env-bspm\" enviroment"
fi

cp bspm.py $IPATH/bspm
chmod 755 $IPATH/bspm

