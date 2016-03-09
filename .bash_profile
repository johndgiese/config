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
if [ $PLATFORM == 'mac' ]; then
    export PATH=/usr/local/bin:/usr/local/sbin:/usr/local/ruby/bin:$PATH
fi
export PATH=$PATH:$HOME/.node/bin


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
alias ipython='ipython --profile=david'

if which pyenv > /dev/null; then
    eval "$(pyenv init -)";
fi

vet () {
    if [ -z "$VIRTUAL_ENV" ]; then
        if [ -f "env/bin/activate" ]; then
            source env/bin/activate
        elif [ -f "../env/bin/activate" ]; then
            source ../env/bin/activate
        elif [ -f "../../env/bin/activate" ]; then
            source ../../env/bin/activate
        elif [ -f "../../../env/bin/activate" ]; then
            source ../../../env/bin/activate
        fi
    else
        deactivate
    fi
}

. ~/.bash/complete/django.sh

function djrs() {(python manage.py runserver $@)}


## GIT
alias gc="git commit"
alias ga="git add"
alias gs="git status"
alias gb="git branch"
alias gm="git merge"
alias gd="git diff"
alias gds="git diff --staged"
alias gp="git push"
alias gl="git pull"
alias gch="git checkout"
alias grh="git reset --hard"
alias glog="git log --oneline"
alias gcp="git cherry-pick"

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
alias tma="tmux attach -t"
. ~/.bash/complete/tma
alias tml="tmux list-sessions"
alias tmn="tmux new-session -s"

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


## FIND REPLACE
function sub (){(ack -l $1 | xargs sed -i '' "s/$1/$2/g")}


## CLEAN WHITE SPACE
alias cws="sed -i.bak -e 's///g' -e 's/ *$//g'"


## WATCH DIRECTORY
if [ $PLATFORM == 'linux' ]; then
    wd () {
        directory=$1
        shift
        command="$@"
        while inotifywait -r -q --format '' -e modify -e create -e delete $directory; do
            $command
        done
    }
elif [ $PLATFORM == 'mac' ]; then
    wd () {
        directory=$1
        shift
        command="$@"
        fswatch -0 -r -o $directory -e __pycache__ -e .cache | xargs -0 -n 1 -I % $command || true
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


## ANSIBLE
alias ap="ansible-playbook -l"


## NVM
function nvm () {
    if hash nvm 2>/dev/null; then
        # source only if the command is used
        export NVM_DIR=~/.nvm
        . $(brew --prefix nvm)/nvm.sh
    fi
    nvm $@
}


## LOCAL STUFF
if [ -f ~/.bash_profile_local ]; then
    source ~/.bash_profile_local
fi
