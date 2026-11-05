#!/usr/bin/env bash

echo "Låt oss spela en gissningslek!"
echo "Varning: Du får inte ändra din gissning. :("

read -r user_guess

function guess() {
  rand=$(( ( RANDOM % 10000 )  + 1337 ))
  if [[ "${1}" -eq "${rand}" ]];
  then
    echo "Rätta"
  else
    echo "Fel"
    exit 1
  fi
}

for _ in {1..1000}; do
  guess "${user_guess}"
done

/readflag