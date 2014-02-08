#!/bin/bash
# requires sudo

cp -uf bin/amodem /usr/local/bin/amodem

if [[ ! -d /usr/local/lib/amodem ]]
then
    mkdir /usr/local/lib/amodem
fi

cp -uf -t /usr/local/lib/amodem lib/*.py
