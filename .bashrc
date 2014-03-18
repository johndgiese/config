# ~/.bashrc: executed by bash(1) for non-login shells.

# If not running interactively, don't do anything
[ -z "$PS1" ] && return


## DETERMINE PLATFORM
if [ $(uname) == 'Linux' ]; then
    PLATFORM='linux'
elif [ $(uname) == 'Darwin' ]; then
    PLATFORM='mac'
elif [ $(uname) == 'NT' ]; then
    PLATFORM='windows'
    export TERM='cygwin'
else
    PLATFORM='unknown'
fi


## BASH HISTORY
HISTCONTROL=ignoreboth
HISTSIZE=1000
HISTFILESIZE=2000
shopt -s histappend


## BASH OPTIONS
# update the values of LINES and COLUMNS after each command
shopt -s checkwinsize

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# enable programmable completion features
if [ $PLATFORM == 'mac' ] && [ -f $(brew --prefix)/etc/bash_completion ]; then
    . $(brew --prefix)/etc/bash_completion
elif [ -f /etc/bash_completion ] && ! shopt -oq posix; then
    . /etc/bash_completion
fi


## PROMPT
# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "$debian_chroot" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# use appropriate prompt
if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
    # have color
    PS1='\[\e]0;\w\a\]${debian_chroot:+($debian_chroot)}\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    # don't have color
    PS1='${debian_chroot:+($debian_chroot)}\w\$ '
fi


## NAVIGATION
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."


## COLORS
export CLICOLOR=yes
export LSCOLORS=ExFxBxDxCxegedabagacad

if [ $PLATFORM == 'linux' ]; then
    alias ls='ls --color=auto'
fi


## VIM
export EDITOR=vim
if [ $PLATFORM == 'linux' ]; then
    function gvim() {(/usr/bin/gvim -f "$@" &)}
elif [ $PLATFORM == 'mac' ]; then
    alias gvim="mvim"
fi


## OPEN FUNCTION
if [ $PLATFORM == 'linux' ]; then
    function op() {
        for var in "$@"
        do
            xdg-open "$var"
        done
    }
elif [ $PLATFORM == 'mac' ]; then
    alias op="open"
elif [ $PLATFORM == 'windows' ]; then
    function op() {
        for var in "$@"
        do
            start "$var"
        done
    }
fi

## WEB-DEVELOPMENT
. ~/.bash/complete/django.sh # setup bash autocomplete

function djrs() {(python manage.py runserver $@)}

## MAC STUFF
if [ $PLATFORM == 'mac' ]; then

    # we want /usr/local/bin before /usr/bin to preference brew binaries
    export PATH=/usr/local/bin:$PATH
    export PATH=/usr/local/sbin:$PATH

    # add node binaries
    export PATH=/usr/local/share/npm/bin:$PATH

    # ruby
    export PATH=/usr/local/opt/ruby/bin:$PATH

    # php
    export PATH="$(brew --prefix josegonzalez/php/php55)/bin:$PATH"
fi

## PYTHON
alias ipython='ipython --profile=david'
if [ $PLATFORM != 'windows' ]; then
    export PYTHONPATH=~/Code/python:$PYTHONPATH

    # auto enter virtual environments
    cd () {
        builtin cd $@
        if [ -f "env/bin/activate" ]; then
            source env/bin/activate
        fi
    }
fi

## CABAL
export PATH=$PATH:$HOME/.cabal/bin


## GIT
alias gc="git commit"
alias gs="git status"
alias gb="git branch"
alias gpush="git push origin master"
alias gpull="git pull origin master"
alias gdiff="git diff"
alias glog="git log --oneline"
function gclone (){(git clone git@github.com:johndgiese/$1.git $2)}
function gcloneh (){(git clone https://github.com/johndgiese/$1 $2)}


