#include <stdio.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char** argv)
{
    if (argc != 6) {
        printf("Usage: /readflag please give me the flag\n");
        return 1;
    }

    char* required[] = { "please", "give", "me", "the", "flag" };

    for (int i = 0; i < 5; i++) {
        if (strcmp(argv[i + 1], required[i]) != 0) {
            printf("Usage: /readflag please give me the flag\n");
            return 1;
        }
    }

    char flag[512] = {0};
    int fd = open("/flag.txt", O_RDONLY);

    if (fd < 0)
        printf("Could not open /flag.txt, if this happens on remote please report!\n");

    read(fd, flag, sizeof(flag));
    close(fd);

    puts(flag);
    return 0;
}
