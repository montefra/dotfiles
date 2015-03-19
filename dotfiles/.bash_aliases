# alias called from .bashrc

#some more ls aliases
alias ll='ls -lh'
alias la='ls -Ah'
alias l='ls -lAh'

#printer
alias lpr_col='lpr -P pe6c'

# alias for my custom rsync with options
alias myrsync='rsync -vahu --progress'

# add coloring, case insensitive and line numbering to grep
alias grep='grep --color -iIn'

# extra non committed aliases
[ -f ~/.bash_aliases_p ] && . ~/.bash_aliases_p
