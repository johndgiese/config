## OPTIONS
shopt -s checkwinsize


## BASHRC
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi


## PLATFORM
if [ $(uname) == 'Linux' ]; then
    PLATFORM='linux'
elif [ $(uname) == 'Darwin' ]; then
    PLATFORM='mac'
    export TERM='xterm-256color'
else
    PLATFORM='unknown'
fi


## PATH
export PATH=/usr/local/bin:/usr/local/sbin:/usr/local/ruby/bin:$PATH:$HOME/.node/bin


## PROMPT
if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
    PS1='\[\e]0;\w\a\]\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='\w\$ '
fi


## HISTORY
HISTCONTROL=ignoreboth
HISTSIZE=500000
HISTFILESIZE=100000
HISTIGNORE='&:?:??:mysql*-p[! ]*'
shopt -s histappend
shopt -s cmdhist
PROMPT_COMMAND='history -a'


## AUTOCOMPLETE
if [ $PLATFORM == 'mac' ] && [ -f $(brew --prefix)/etc/bash_completion ]; then
    . $(brew --prefix)/etc/bash_completion
elif [ -f /etc/bash_completion ] && ! shopt -oq posix; then
    . /etc/bash_completion
fi


## NAVIGATION
shopt -s autocd 2> /dev/null
shopt -s dirspell 2> /dev/null
shopt -s cdspell 2> /dev/null

CDPATH=".:~/Projects"

alias ..="cd ../"
alias ...="cd ../../"
alias ....="cd ../../../"
alias .....="cd ../../../../"

## COLORS
if [ $PLATFORM == 'linux' ]; then
    alias ls='ls --color=auto'
elif [ $PLATFORM == 'mac' ]; then
    export CLICOLOR=yes
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


## PYTHON
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if which pyenv > /dev/null; then
    eval "$(pyenv init -)";
fi

if which pyenv-virtualenv-init > /dev/null; then
    eval "$(pyenv virtualenv-init -)"
fi

if [ $PLATFORM == 'mac' ]; then
    # necessary so that pyenv creates framework builds of python, which is in
    # turn necessary so that vim can use python for auto complete, etc.
    export PYTHON_CONFIGURE_OPTS="--enable-framework"
fi


## GIT
alias gc="git commit"
alias gca="git commit --amend"
alias gcn="git commit --no-verify"
alias ga="git add"
alias gs="git status"
alias gb="git branch"
alias gm="git merge"
alias gd="git diff"
alias gds="git diff --staged"
alias gp="git push"
alias gpu="git pull"
alias gch="git checkout"
alias grh="git reset HEAD"
alias glog="git log --oneline"
alias gcp="git cherry-pick"

function gpb() {
    git push --set-upstream origin `git rev-parse --abbrev-ref HEAD`
}

if hash __git_complete 2>/dev/null; then
    __git_complete gc _git_commit
    __git_complete ga _git_add
    __git_complete gb _git_branch
    __git_complete gm _git_merge
    __git_complete gd _git_diff
    __git_complete gch _git_checkout
    __git_complete gcp _git_cherry_pick
fi


## MAN
export MANWIDTH=100


## TMUX
alias tml="tmux list-sessions"

function tma() {
    current_directory=${PWD##*/}
    current_directory_specials_removed=${current_directory//[.]/_}
    tmux_create_or_join ${1:-$current_directory_specials_removed}
}

function tmux_create_or_join() {
    if hash tmux 2>/dev/null; then
        if [ -z "$TMUX" ]; then
            if tmux has-session -t $1; then
                tmux attach-session -t $1
            else
                tmux new-session -s $1
            fi
        fi
    else
        echo 'tmux is not installed' && exit 1
    fi
}

# Auto join a tmux session upon ssh-ing into a server
if [ -n "$SSH_CLIENT" ]; then
    tmux_create_or_join $USER
fi


## SUBSTITUTION UTILS
function sub (){(ag -l "$1" | xargs sed -i '' "s/$1/$2/g")}
function ren (){(find . -type f -name "*$1*" -exec rename "s/$1/$2/" {} \;)}
function sar (){(sub "$1" "$2" ; ren "$1" "$2")}
alias cws="sed -i.bak -e 's///g' -e 's/ *$//g'"


## WATCH DIRECTORY
if [ $PLATFORM == 'linux' ]; then
    wd () {
        directory=$1
        echo "Watching directory $directory"
        echo "Scanning for files to ignore"
        # TODO: get this to ignore .git folder files too
        excludes="$(find . -exec git check-ignore -q {} \; -exec echo --exclude {} \; -prune 2> /dev/null)"
        events='-e move -e create -e delete -e modify'
        command=$2
        echo "Setting up watches"
        while inotifywait -r -q --format '' $events $excludes $directory; do
            eval $command || true
        done
    }
elif [ $PLATFORM == 'mac' ]; then
    wd () {
        directory=$1
        excludes=$(find . -exec git check-ignore {} \; -exec echo -e {} \; -prune)
        shift
        command="$@"
        fswatch -0 -r -o $directory $excludes | xargs -0 -n 1 -I % $command || true
    }
fi


## CD SUB
cds () {
    sub="$(find . -name $1 -type d -print -quit)"
    if [ -n "$sub" ]; then
        cd $sub
    else
        echo "No subdirectory named $1"
    fi
}


## NVM
function nvm () {
    if hash nvm 2>/dev/null; then
        # source only if the command is used
        export NVM_DIR="$HOME/.nvm"
        . "/usr/local/opt/nvm/nvm.sh"
    fi
    nvm $@
}


## LOCAL STUFF
if [ -f ~/.bash_profile_local ]; then
    source ~/.bash_profile_local
fi


## C++
export PKG_CONFIG_PATH="$PKG_CONFIG_PATH:/usr/local/lib/pkgconfig/"
