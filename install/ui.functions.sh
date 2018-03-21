trap "/bin/kill -- -$BASHPID &>/dev/null" EXIT INT TERM

toggle_spin() {
        if [ -z "$spin_pid" ]; then
            (
                i=1
                sp="/-\|"
                printf " "
                while true;
                do
                    printf "\b[1m${sp:i++%${#sp}:1}[0m"
                    if [[ i -eq ${#sp} ]]; then
                        i=0
                    fi
                    sleep 0.2
                done
            ) &
            sleep 1
            spin_pid=$!
        else
            sleep 1
            kill $spin_pid
            wait $spin_pid 2>/dev/null
            printf "\b"
            unset spin_pid
        fi
}

title() {
    printf "\n > $1\n"
}

doing() {
    if [ -z "$2" ]; then
        pad=12
    else
        pad=$2
    fi
    printf "    [36m%${pad}s[0m ... " "$1"
    toggle_spin
}

say_done() {
    toggle_spin
    if [ $1 -gt 0 ]; then
        echo '[31mFAIL[0m'
        exit 1
    else
        echo '[32mOK[0m '
    fi
}
