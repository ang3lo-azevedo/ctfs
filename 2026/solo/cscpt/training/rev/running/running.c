// gcc running.c -o running -no-pie -m32

#include<stdio.h>
#include<string.h>

char string[3*24] = {67, 11, 67, 83, 232, 22, 67, 204, 215, 80, 42, 23, 84, 65, 90, 123, 218, 174, 85, 99, 107, 109, 34, 116, 95, 51, 109, 107, 28, 221, 109, 43, 209, 95, 55, 20, 100, 129, 135, 101, 192, 198, 95, 177, 159, 99, 179, 75, 97, 25, 65, 100, 165, 18, 97, 80, 79, 95, 6, 103, 118, 97, 164, 101, 214, 208, 122, 128, 217, 125, 179, 76};

int main(int argc, char* argv[]){
    int steps = 0;
    int i;

    if(argc != 2){
        puts("Usage: ./running <flag>");
        return 0;
    }

    if (strlen(argv[1]) != 24){
        puts("You should walk before you run");
        return 0;
    }

    for(i=0; i<strlen(argv[1]); i++){
        
        if (argv[1][i] != string[(i*3)]){
            puts("Next time you might finish the race");
            return 0;
        }
        steps += 1;
        printf("Mile %d. Keep running\n", steps);
    }

    printf("GOOD JOB: You got the flag for running %d miles\n", steps);
}