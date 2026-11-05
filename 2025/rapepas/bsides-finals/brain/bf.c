#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TAPE_SIZE 1000000

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <brainfuck_file>\n", argv[0]);
        return 1;
    }

    // Read the file
    FILE *file = fopen(argv[1], "r");
    if (!file) {
        perror("Error opening file");
        return 1;
    }

    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    char *code = (char *)malloc(file_size + 1);
    fread(code, 1, file_size, file);
    code[file_size] = '\0';
    fclose(file);

    // Initialize tape
    unsigned char *tape = (unsigned char *)calloc(TAPE_SIZE, sizeof(unsigned char));
    int ptr = 0;
    int code_ptr = 0;

    // Execute
    while (code_ptr < file_size) {
        switch (code[code_ptr]) {
            case '>':
                ptr++;
                if (ptr >= TAPE_SIZE) ptr = 0;
                break;
            case '<':
                ptr--;
                if (ptr < 0) ptr = TAPE_SIZE - 1;
                break;
            case '+':
                tape[ptr]++;
                break;
            case '-':
                tape[ptr]--;
                break;
            case '.':
                putchar(tape[ptr]);
                fflush(stdout);
                break;
            case ',':
                tape[ptr] = getchar();
                break;
            case '[':
                if (tape[ptr] == 0) {
                    int depth = 1;
                    while (depth > 0) {
                        code_ptr++;
                        if (code[code_ptr] == '[') depth++;
                        if (code[code_ptr] == ']') depth--;
                    }
                }
                break;
            case ']':
                if (tape[ptr] != 0) {
                    int depth = 1;
                    while (depth > 0) {
                        code_ptr--;
                        if (code[code_ptr] == ']') depth++;
                        if (code[code_ptr] == '[') depth--;
                    }
                }
                break;
        }
        code_ptr++;
    }

    free(tape);
    free(code);
    return 0;
}
