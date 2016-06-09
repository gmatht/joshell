filetype plugin on

call plug#begin('~/.vim/plugged')

" Make sure you use single quotes

" Shorthand notation; fetches https://github.com/junegunn/vim-easy-align
" Plug 'junegunn/vim-easy-align'

" Any valid git URL is allowed
" Plug 'https://github.com/junegunn/vim-github-dashboard.git'

" Group dependencies, vim-snippets depends on ultisnips
" Plug 'SirVer/ultisnips' | Plug 'honza/vim-snippets'

" On-demand loading
Plug 'scrooloose/nerdtree', { 'on':  'NERDTreeToggle' }
Plug 'tpope/vim-fireplace', { 'for': 'clojure' }

" Using a non-master branch
Plug 'rdnetto/YCM-Generator', { 'branch': 'stable' }

" Using a tagged release; wildcard allowed (requires git 1.9.2 or above)
Plug 'fatih/vim-go', { 'tag': '*' }

" Plugin options
Plug 'nsf/gocode', { 'tag': 'v.20150303', 'rtp': 'vim' }

" Plugin outside ~/.vim/plugged with post-update hook
Plug 'junegunn/fzf', { 'dir': '~/.fzf', 'do': './install --all' }


function! DoRemote(arg)
  UpdateRemotePlugins
endfunction
Plug 'Shougo/deoplete.nvim', { 'do': function('DoRemote') }
" Plug 'https://github.com/Shougo/deoplete.nvim.git', { 'do': function('DoRemote') }
Plug 'zchee/deoplete-jedi'

Plug 'let-def/ocp-indent-vim'

" Unmanaged plugin (manually installed and updated)
Plug '~/my-prototype-plugin'

" Add plugins to &runtimepath
call plug#end()
"set runtimepath+=$XDG_CONFIG_HOME/nvim/plugged/deoplete.nvim
"set runtimepath+='
"set runtimepath+=/home/john/.config/nvim/Shougo/deoplete.nvim

let g:deoplete#enable_at_startup = 1
set runtimepath+=~/.vim/plugged/deoplete.nvim

set completeopt+=noinsert,noselect
set completeopt-=preview
set omnifunc=syntaxcomplete#Complete

hi Pmenu    gui=NONE    guifg=#c5c8c6 guibg=#373b41
hi PmenuSel gui=reverse guifg=#c5c8c6 guibg=#373b41

let g:deoplete#enable_at_startup = 1


" Let <Tab> also do completion
inoremap <silent><expr> <Tab>
\ pumvisible() ? "\<C-n>" :
\ deoplete#mappings#manual_complete()

" call remote#host#RegisterPlugin('python3', '/home/john/.config/nvim/Shougo/deoplete.nvim/rplugin/python3/deoplete', [
"      \ {'sync': v:true, 'name': '_deoplete', 'opts': {}, 'type': 'function'},
"    \ ])
"
"
call remote#host#RegisterPlugin('python3', '/home/john/.vim/plugged/deoplete.nvim/rplugin/python3/deoplete', [
      \ {'sync': v:true, 'name': '_deoplete', 'opts': {}, 'type': 'function'},
    \ ])




"For OCaml
" let g:opamshare = substitute(system('opam config var share'),'\n$','','''')
"execute "set rtp+=" . g:opamshare . "/merlin/vim"
" set rtp^="%{share}%/ocp-indent/vim"
set rtp+=/usr/local/share/ocamlmerlin/vim
filetype plugin indent on


