# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

# the default umask is set in /etc/profile; for setting the umask
# for ssh logins, install and configure the libpam-umask package.
#umask 022

# Most applications support several languages for their output.
# To make use of this feature, simply uncomment one of the lines below or
# add your own one (see /usr/share/locale/locale.alias for more codes)
# This overwrites the system default set in /etc/sysconfig/language
# in the variable RC_LANG.
#
#export LANG=de_DE.UTF-8	# uncomment this line for German output
#export LANG=fr_FR.UTF-8	# uncomment this line for French output
#export LANG=es_ES.UTF-8	# uncomment this line for Spanish output

# opensuse settings
if [ -d /etc/os-release ]
then
  . /etc/os-release
else
  NAME=""
fi

if [ $NAME = "openSUSE" ]
then
  test -z "$PROFILEREAD" && . /etc/profile || true
fi

# if running bash, from kubuntu, use it also in opensuse
if [ -n "$BASH_VERSION" ]; then
    # include .bashrc if it exists
    if [ -f "$HOME/.bashrc" ]; then
	. "$HOME/.bashrc"
    fi
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi
if [ -d $HOME/.local/bin ]
then
  export PATH=$HOME/.local/bin:"${PATH}"
fi
if [ -d $HOME/.gem/ruby/2.1.0/bin ]
then
  export PATH=$HOME/.gem/ruby/2.1.0/bin:"${PATH}"
fi
if [ -d $HOME/.gem/ruby/2.0.0/bin ] ; then
    PATH=$HOME/.gem/ruby/2.0.0/bin:"${PATH}" 
fi
if [ -d $HOME/.cabal/bin ] ; then
    PATH=$HOME/.cabal/bin:"${PATH}"
fi