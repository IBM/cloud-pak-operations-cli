_cpo_completion() {
    local IFS=$'\n'
    local response

    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _CPO_COMPLETE=bash_complete $1)

    for completion in $response; do
        IFS=',' read type value <<< "$completion"

        if [[ $type == 'dir' ]]; then
            COMREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMREPLY=()
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}

_cpo_completion_setup() {
    complete -o nosort -F _cpo_completion cpo
}

_cpo_completion_setup

