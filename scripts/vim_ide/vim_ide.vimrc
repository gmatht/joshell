:map ; <Esc>:w<CR>
:map <F2> <Esc>:w<CR>:!%:p<CR>
:map <F3> <Esc>:w<CR>:!make run<CR>
:map ; <Esc>:exe "!bash openline.sh " . line(".")<CR>
:map <F12> <Esc>:exe "!bash openline.sh " . line(".")<CR>
:set tabstop=8
filetype plugin on
set omnifunc=syntaxcomplete#Complete
:color desert


"for OCaml
let g:opamshare = substitute(system('opam config var share'),'\n$','','''')
execute "set rtp+=" . g:opamshare . "/merlin/vim"
" set rtp^="%{share}%/ocp-indent/vim"

"execute "helptags " . substitute(system('opam config var share'),'\n$','','''') .  "/merlin/vim/doc"


if !exists('g:merlin') | let g:merlin = {} | endif | let s:c = g:merlin
let g:merlin_ignore_warnings = "false"

let s:c.merlin_home = expand('<sfile>:h:h:h:h')

" Highlight the expression which type is given
" hi def link EnclosingExpr IncSearch
"

echo 'Old vim, use C-x C-o in insert mode to complete'
