if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

# source virtualenv if shell is opened in one (using customized cd function)
cd . > /dev/null
