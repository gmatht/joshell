#!/bin/bash
# install neovim
hash nvim || (
	sudo apt-get install software-properties-common
	sudo add-apt-repository ppa:neovim-ppa/unstable
	sudo apt-get update
	sudo apt-get install neovim
)

#install python3 for neovim
hash pip3 ||
	sudo apt-get install pip3 ||
	sudo apt-get install python3-pip
pip3 install neovim

#install plug.vim
[ -s  ~/.config/nvim/autoload/plug.vim ] || curl -fLo  ~/.config/nvim/autoload/plug.vim --create-dirs http://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

#Java
#We can just use an old version of javacomplete that doesn't need jdk8
true || java -version 2>&1 | grep 1.8 || sudo apt-get install openjdk-8-jdk || 
	java -version 2>&1 | grep 1.8 || (
	sudo add-apt-repository ppa:webupd8team/java -y
	sudo apt-get update
	sudo apt-get install oracle-java8-installer
	sudo apt-get install oracle-java8-set-default
)

#perldoc
sudo apt-get install perl-doc

#This doesn't seem to always work? Do it twice to make sure
nvim -u vim_ide.nvimrc +"PlugInstall" +UpdateRemotePlugins +qall
nvim -u vim_ide.nvimrc +"PlugInstall" +UpdateRemotePlugins +qall

echo About to install OCaml support. Press Enter to Continue, or Ctrl-C to quit
read

### for OCaml ###
#* ocp-indent
sudo apt-get install python-dev python-pip python3-dev opam pkg-config camlp4
[ -e ~/.opam ] || opam init https://opam.ocaml.org/`opam --version|grep -o ^...`
eval `opam config env`
# On Ubuntu 16.04, installing camlp4 via opam break
opam pin add camlp4 /usr/bin/camlp4
opam install ocp-indent
vim -u vim_ide.vimrc +"PlugInstall" +qall

## Merlin 
# Current opam version of Merlin only supports python2
# We could install the old vim with python2 support
# But lets install merlin from git with python3 support
#vim --version | fgrep '+python ' || sudo apt-get install vim-nox-py2
(
	mkdir build 
	cd build/ 
	git clone https://github.com/the-lambda-church/merlin.git 
	cd merlin/ 
	. ~/.opam/opam-init/init.sh 
	opam install ppx_deriving 
	./configure  
	nice make -j2 
	sudo make install
	PATH="/usr/local/bin/:$PATH" nvim -u vim_ide.nvimrc
)

#We didn't seem to need to do the following with the new merlin:
#echo ':execute "helptags " . g:opamshare . "/merlin/vim/doc" | nvim

#Something in this script seem to mess up cutting and pasting from the terminal.
stty sane
echo Install Finished, Press Enter to exit
read
tput reset
