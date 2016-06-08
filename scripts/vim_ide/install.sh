#install neovim
#CHECK this is needed if we do pip install too?
#sudo apt-get install software-properties-common
#sudo add-apt-repository ppa:neovim-ppa/unstable
#sudo apt-get update
#sudo apt-get install neovim

#install python3 for neovim
sudo apt-get install pip3
pip3 install neovim

#install plug.vim
 
curl -fLo  ~/.config/nvim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

nvim -u mynvim.plug.rc +"PlugInstall" +qall

#for OCaml
sudo apt-get install python-dev python-pip python3-dev python3-pip opam
opam init https://opam.ocaml.org/`opam --version|grep -o ^...`
opam install ocp-indent merlin
nvim -u mynvim.plug.rc +"PlugInstall" +qall
(echo ':execute "helptags " . g:opamshare . "/merlin/vim/doc"
'
sleep 3
echo ':q
') | ocaml_ide.sh 
