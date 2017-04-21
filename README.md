# My operating system configuration.

Has files for Mac, Linux, and Windows.

Everything is stored in a repo with the .gitignore file set to ignore everything; for this reason whenever you want to add something you need to force it.

## Installation

    cd ~
    git clone https://github.com/johndgiese/config
    cd config
    mv * .[^.]* ..
    cd ..
    rm -rf config

If you want to use the basic vimrc create a symlink

    ln -s .vimrc-basic .vimrc

## Tmux

I use tmux most of the time.  My `.tmux.conf` file customizes tmux a bit.  My `.bash_profile` will auto attach to a tmux session with the name `$USER` upon SSH-ing into a server.  This is convenient because 99% of the time I am in a remote server I want to have a tmux session live in case my connection fails.

I also have two tmux aliases:

- `tma` (for "tmux attach").  If no argument is given, attach to a session named after the current folder; if no such session exists, create one.  On my dev laptop I usually have a tmux session per project.  If you provide a single argument, attach to that name.  This alias has tab completion.
- `tml` (for "tmux list").  List your current tmux sessions.

## SSH

I use an ssh-agent to forward my ssh credentials; its nice for pulling code on remote servers.  My `.bash_profile` runs `ssh-add` on startup.
