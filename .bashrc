# ~/.bashrc: executed by bash(1) for non-login shells.

# If not running interactively, don't do anything
[ -z "$PS1" ] && return


## DETERMINE PLATFORM
if [ $(uname) == 'Linux' ]; then
    PLATFORM='linux'
elif [ $(uname) == 'Darwin' ]; then
    PLATFORM='mac'
    export TERM='xterm-256color'
else
    PLATFORM='unknown'
fi


## BASH HISTORY
HISTCONTROL=ignoreboth
HISTSIZE=5000
HISTFILESIZE=10000
HISTIGNORE='&:?:??:mysql*-p[! ]*'
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

if [ $PLATFORM == 'linux' ]; then
    alias ls='ls --color=auto'
elif [ $PLATFORM == 'mac' ]; then
    export CLICOLOR=yes
fi


## VIM
export EDITOR=vim
if [ $PLATFORM == 'linux' ]; then
    function gvim() {(/usr/bin/gvim -f "$@" &)}
elif [ $PLATFORM == 'mac' ]; then
    alias gvim="mvim"
    alias vim="mvim -v"
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
    export PATH=$HOME/.node/bin:$PATH

    # ruby
    export PATH=/usr/local/opt/ruby/bin:$PATH

fi

## PYTHON
alias ipython='ipython --profile=david'
# auto enter virtual environments
cd () {
    builtin cd "$@"
    if [ -f "env/bin/activate" ]; then
        source env/bin/activate
    elif [ -f "../env/bin/activate" ]; then
        source ../env/bin/activate
    elif [ -f "../../env/bin/activate" ]; then
        source ../../env/bin/activate
    elif [ -f "../../../env/bin/activate" ]; then
        source ../../../env/bin/activate
    fi
}



## CABAL
export PATH=$PATH:$HOME/.cabal/bin

## GIT
alias gc="git commit"
alias gs="git status"
alias gb="git branch"
alias gd="git diff"
alias gch="git checkout"
alias grh="git reset --hard"
alias glog="git log --oneline"
alias gcp="git cherry-pick -x"

if hash __git_complete 2>/dev/null; then
    __git_complete gc _git_commit
    __git_complete gb _git_branch
    __git_complete gd _git_diff
    __git_complete gch _git_checkout
    __git_complete gcp _git_cherry_pick
fi

## MAN
export MANWIDTH=100

## TMUX
alias tma="tmux attach -t"
. ~/.bash/complete/tma
alias tml="tmux list-sessions"
alias tmn="tmux new-session -s"

## FIND REPLACE
function sub (){(ack -l $1 | xargs sed -i '' "s/$1/$2/g")}

## UTILS

# clean white space
alias cws="sed -i.bak -e 's///g' -e 's/ *$//g'"

# watch a directory and run the specified command if any files change
wd () {
    directory=$1
    shift
    command=$@
    while inotifywait -r -q --format '' -e modify -e create -e delete $directory; do
        $command
    done
}

## COOL SHORTCUT COMMANDS
cds () {
    sub="$(find . -name $1 -type d -print -quit)"
    if [ -n "$sub" ]; then
        cd $sub
    else
        echo "No subdirectory named $1"
    fi
}

vims () {
    sub="$(find . -name $1 -type f -print -quit)"
    if [ -n "$sub" ]; then
        vim $sub
    else
        echo "No file named $1"
    fi
}

## Ansible
alias ap="ansible-playbook -l"

## Hook for local bash stuff
if [ -f ~/.bashrc_local ]; then
    source ~/.bashrc_local
fi

## Tmux auto login
# If tmux command exists, and you aren't in a session, then create one using
# the current user's name (or join it if it exists)
if hash tmux 2>/dev/null; then
    if [ -z "$TMUX" ] && [ -n "$SSH_CLIENT" ]; then
        if tmux has-session -t $USER; then
            tmux attach-session -t $USER
        else
            tmux new-session -s $USER
        fi
    fi
fi
