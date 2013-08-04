# My operating system configuration.

Has files for Mac, Linux, and Windows.

Everything is stored in a repo with the .gitignore file set to ignore everything; for this reason whenever you want to add something you need to force it.

Here is how I usually install it:

    cd ~
    git clone https://github.com/johndgiese/config
    cd config
    mv * .[^.]* ..
    cd ..
    rm -rf config
