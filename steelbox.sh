# Copyright (C) 2022 Kamal Curi
# Full license inside the manual at doc/

#!/usr/bin/env bash

version="1.21"

echo "Steelbox V$version, Copyright (C) 2022 Kamal Curi"
echo "Steelbox comes with ABSOLUTELY NO WARRANTY; For license details, read the manual in doc/"


if [ -f $HOME/.pasfile.csv.gpg ]
then
    gpg $HOME/.pasfile.csv.gpg &> /dev/null
    if [ $? -gt 0 ]
    then
        echo WRONG PASSWORD!
        exit 1
    fi
    rm $HOME/.pasfile.csv.gpg
else
    echo ERROR: NO ENCRYPTED PASSWORD FILE FOUND
    echo STEELBOX WILL ATTEMPT TO OPEN UNENCRYPTED FILE
    echo PRESS ENTER TO CONTINUE.
    read
fi

python3 /opt/steelbox.py $version

gpg -c --no-symkey-cache --cipher-algo AES256 $HOME/.pasfile.csv

if [ $? -gt 0 ]
then
    echo ERROR ENCRYPTING PASSWORD FILE!
    echo UNENCRYPTED FILE IN $HOME/.pasfile.csv
    echo PRESS ENTER TO QUIT
    read
    exit 1
fi
rm $HOME/.pasfile.csv
