# My operating system configuration.

Has files for Mac, Linux, and Windows.

Everything is stored in a repo with the .gitignore file set to ignore everything; for this reason whenever you want to add something you need to force it.

# Installation

    cd ~
    git clone https://github.com/johndgiese/config
    cd config
    mv * .[^.]* ..
    cd ..
    rm -rf config

If you want to use the basic vimrc create a symlink

    ln -s .vimrc-basic .vimrc
