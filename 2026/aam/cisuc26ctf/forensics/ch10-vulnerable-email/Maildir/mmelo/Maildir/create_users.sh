#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo "Execute como root: sudo $0 users.txt"
    exit 1
fi

FILE="${1:?Informe o arquivo de usuários}"

while IFS=: read -r USERNAME PASSWORD; do
    [[ -z "$USERNAME" || "$USERNAME" == \#* ]] && continue  # ignora linhas vazias e comentários

    echo "==> Criando: $USERNAME"

    if id "$USERNAME" &>/dev/null; then
        echo "    [AVISO] Já existe, pulando."
    else
        useradd -m -s /bin/bash "$USERNAME"
        echo "$USERNAME:$PASSWORD" | chpasswd
    fi

    MAILDIR="/home/$USERNAME/Maildir"
    mkdir -p "$MAILDIR"/{new,cur,tmp}
    chown -R "$USERNAME:$USERNAME" "$MAILDIR"
    chmod -R 700 "$MAILDIR"

    echo "    [OK] Concluído para $USERNAME"

done < "$FILE"
