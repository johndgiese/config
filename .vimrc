"GENERAL SETTINGS
set autoindent
set showmatch
set ruler
set laststatus=2
set backspace=indent,eol,start
set showmode
set tabstop=4 softtabstop=4 shiftwidth=4 expandtab
set history=1000
set encoding=utf-8
set noswapfile

" better <ESC> (to go back to normal mode from insert mode)
inoremap jk <ESC>
inoremap <ESC> <nop>

" switch semi-colon and colon
nnoremap ; :
vnoremap ; :
nnoremap : ;
vnoremap : ;

" insert the very magic reg-ex mode every time
set hlsearch incsearch
nnoremap / /\v
nnoremap ? ?\v
nnoremap <silent> <leader>/ :noh<CR>

" set paste toggle
set pastetoggle=<leader>p

nnoremap <A-]> :cnext<CR>
nnoremap <A-[> :cprev<CR>

" Move between editor lines (instead of actual lines) when holding CTRL
vnoremap j gj
vnoremap k gk
vnoremap $ g$
vnoremap ^ g^
vnoremap 0 g0
nnoremap j gj
nnoremap k gk
nnoremap $ g$
nnoremap ^ g^
nnoremap 0 g0

" jumping to definitions

" goto definition
nnoremap gd <C-]>zz

" go back
nnoremap gb <C-t>

" making vim command line more like bash
cnoremap <C-a> <Home>
cnoremap <C-e> <End>
cnoremap <C-b> <Left>
cnoremap <C-f> <Right>
cnoremap <M-b> <S-Left>
cnoremap <M-f> <S-Right>

" buffer switching
nnoremap <silent> [b :bprevious<CR>
nnoremap <silent> ]b :bnext<CR>
nnoremap <silent> [B :bfirst<CR>
nnoremap <silent> ]B :blast<CR>

" window switching
" moving using M-direction
" open new windows ugin M-S-direction
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-h> <C-w>h
nnoremap <C-l> <C-w>l

" Highlight whitespace with <leader>w, and remove with <leader>W
nnoremap <leader>w :/\s\+$<CR>
nnoremap <leader>W :%s/\s\+$//e<CR><silent>:noh<CR>

" SPELLING
" toggle spell checking
nnoremap <silent> <leader>s :set spell!<CR>

" correct the current word and move to the next one using ,S
nnoremap <silent> <leader>S 1z=]s
