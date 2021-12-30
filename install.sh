#!/usr/bin/env bash

echo Steelbox install

echo Copying steelbox.sh
sudo cp -f steelbox.sh /opt/steelbox.sh
if [ $? -gt 0 ]
then
    echo COULD NOT COPY STEELBOX.SH
    echo QUITTING
    exit 1
fi

echo Copying steelbox.py
sudo cp -f steelbox.py /opt/steelbox.py
if [ $? -gt 0 ]
then
    echo COULD NOT COPY STEELBOX.PY
    echo QUITTING
    sudo rm /opt/steelbox.sh
    exit 1
fi
echo Copying Help file
sudo cp -f sbhelp /opt/sbhelp
if [ $? -gt 0 ]
then
    echo COULD NOT COPY HELP FILE
    echo QUITTING
    sudo rm /opt/steelbox.sh
    sudo rm /opt/steelbox.py
    exit 1
fi
echo Setting up permissions
sudo chmod +x /opt/steelbox.sh
if [ $? -gt 0 ]
then
    echo COULD NOT SET PERMISSIONS
    echo QUITTING
    sudo rm /opt/steelbox.sh
    sudo rm /opt/steelbox.py
    sudo rm /opt/sbhelp
    exit 1
fi

echo Creating symbolic link to /usr/bin
if [ ! -f /usr/bin/steelbox ]
then
    sudo ln -s /opt/steelbox.sh /usr/bin/steelbox
    if [ $? -gt 0 ]
    then
        echo COULD NOT CREATE LINK
        echo QUITTING
        sudo rm /opt/steelbox.sh
        sudo rm /opt/steelbox.py
        sudo rm /opt/sbhelp
        exit 1
    fi
fi

if [ ! -f $HOME/.pasfile.csv.gpg ] && [ ! -f $HOME/.pasfile.csv ]
then
    echo Creating initial password file
    touch $HOME/.pasfile.csv
    if [ $? -gt 0 ]
    then
        echo COULD NOT CREATE PASSWORD FILE
        echo QUITTING
        sudo rm /opt/steelbox.sh
        sudo rm /opt/steelbox.py
        sudo rm /usr/bin/steelbox
        sudo rm /opt/sbhelp
        exit 1
    fi
    echo Setting up password file
    echo service,user,pswd > $HOME/.pasfile.csv &> /dev/null

    echo Loading GPG to encrypt the file for the first time.
    echo ===========================================================
    echo YOU WILL BE ASKED TO GIVE A PASSWORD TO THE PASSWORD FILE
    echo \(And yes, I\'m not immune to the irony\)
    echo YOU WILL NEED THIS PASSWORD TO OPEN YOUR FILE
    echo gpg-agent \(OR WHATEVER AGENT YOU USE\) WILL
    echo HANDLE YOUR PASSWORDS UNTIL YOU REBOOT
    echo ===========================================================
    echo PRESS ENTER TO CONTINUE
    read

    gpg -c --cipher-algo AES256 $HOME/.pasfile.csv
    if [ $? -gt 0 ]
    then
        echo ERROR ENCRYPTING THE FILE
        echo YOU MUST TYPE A PASSWORD FOR THE INITIAL PASSWORD FILE
        echo DELETING ALL INSTALATION FILES
        sudo rm /opt/steelbox.sh
        sudo rm /opt/steelbox.py
        sudo rm /usr/bin/steelbox
        sudo rm /opt/sbhelp
        rm $HOME/.pasfile.csv
        exit 1
    fi
    rm $HOME/.pasfile.csv
fi