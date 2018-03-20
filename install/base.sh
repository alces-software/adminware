admin() {
  (cd /opt/adminware && PATH="/opt/adminware/opt/ruby/bin:$PATH" bin/adminware "$@")
}

if [ "$ZSH_VERSION" ]; then 
  export admin
else
  export -f admin
fi
alias adm=admin

if [ "$BASH_VERSION" ]; then
  _admin() {
    local cur="$2" cmds input cur_ruby

    if [[ -z "$cur" ]]; then
      cur_ruby="__CUR_IS_EMPTY__"
    else
      cur_ruby=$cur
    fi

    cmds=$(
      cd /opt/adminware &&
      PATH="/opt/adminware/opt/ruby/bin:$PATH"
      bin/autocomplete $cur_ruby ${COMP_WORDS[*]}
    )

    COMPREPLY=( $(compgen -W "$cmds" -- "$cur") )
  }
  complete -o default -F _admin admin ad
fi
