# THIS REPO IS **NOT** UP-TO-DATE

# This project is now hosted  [here](http://vps41059.publiccloud.com.br:3000/brejela/steelbox)

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

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PUR-
POSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Founda-
tion, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
USA.
