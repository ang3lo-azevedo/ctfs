from hashlib import sha256
from os import environ
from secrets import choice


NUM_ROUNDS = 100


def verify(commitment: bytes, message: bytes, unveil_info: tuple[bytes, bytes]) -> bool:
    """
    Check if a commitment was correctly unveiled.

    :param commitment: The commitment that was unveiled
    :param message: The message the commitment was unveiled to
    :param unveil_info: The unveil information used to unveil the commitment

    :return: Whether the commitment was correctly unveiled
    """

    r1, r2 = unveil_info  # two is better than one, right?

    return commitment == sha256(r1 + message + r2).digest()


def main():
    print("I want to play a game...")
    already_seen = {}
    for _ in range(NUM_ROUNDS):
        com = bytes.fromhex(input("Commitment (hex): "))
        my_choice = choice(["rock", "paper", "scissors"])
        print(f"I choose {my_choice}.")
        your_choice = input("What did you choose? ")
        if your_choice not in {"rock", "paper", "scissors"}:
            print("*Your opponent just staress at you, seeming very confused*")
            return
        unveil_info = tuple(bytes.fromhex(x) for x in input("Proof (hex): ").split())
        if not verify(com, your_choice.encode("ascii"), unveil_info):
            print("Hey, no cheating! Do that again and I will eat all your flags")
            return
        elif my_choice == your_choice:
            print("Sorry, that was a draw. No flag for you")
            return
        elif (my_choice, your_choice) in {
            ("rock", "scissors"),
            ("scissors", "paper"),
            ("paper", "rock"),
        }:
            print("Sorry, you lose. No flag for you")
            return
        elif com in already_seen and already_seen[com] != your_choice:
            print("Something fishy is going on here. What are you doing?")
            return
        already_seen[com] = your_choice
    print(f"How can that be? Well, a deal is a deal. Here is your flag: {environ['FLAG']}")


if __name__ == "__main__":
    main()
