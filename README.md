# Steelbox
## Because sometimes you just want a password manager

Steelbox is a password manager that runs under your terminal, with GnuPG.


## **ATTENTION: It is recommended you run steelbox under [st](https://st.suckless.org/) or [alacritty](https://alacritty.org/)**

### Installation (and upgrade):
Just run `install.sh` **WITHOUT SUDO**

### To remove Steelbox:
Just run `install.sh remove` **WITHOUT SUDO**

### Upgrading
If you're upgrading Steelbox, don't worry: `install.sh` will do it automatically without messing with your password file

#### Dependencies:
Clipboard support needs the [pyperclip](https://pypi.org/project/pyperclip/) module. You can install it with [pip](https://pypi.org/project/pip/):

`pip3 install pyperclip`

Also for clipboard support, you need [xclip](https://github.com/astrand/xclip) or [xsel](https://github.com/kfish/xsel) on your machine.

This program has no support for the wayland clipboard... Unless pyperclip starts supporting it :P

The standard ( this program was made with v3.10 ) python installation comes with the `curses` and `csv` modules, just make sure you have [GnuPG](https://gnupg.org/) installed.