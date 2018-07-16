# alias called from .bashrc

#some more ls aliases
alias ll='ls -lh'
alias la='ls -Ah'
alias l='ls -lAh'

# alias for my custom rsync with options
alias myrsync='rsync -vahu --progress'

# add coloring, case insensitive and line numbering to grep
alias grep='grep --color -iIn'

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# extra non committed aliases
[ -f ~/.bash_aliases_p ] && . ~/.bash_aliases_p
