/*
 * Can you rally the team and remind the CEO who is shipping the product?
 *
 * The CEO just closed a funding round and emptied a bottle of wine too much
 * with the stakeholders.
 * Enough slack despite the sprint to play a round of "CEOnnect Four",
 * their favorite team alignment activity.
 * But careful: the CEO doesn't take feedback well...
 * Can you push to prod nevertheless?
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

#define XDIM 7
#define YDIM 6


struct game_state {
    char f[YDIM][XDIM];  // [y][x]
    int played;  // amount of played moves
    struct hist_moves *hist;
};

struct player_data {
    char name[8];
    void (*end_fns[4]) (void);
};

struct ceo_data {
    char s[5][8];
};

struct hist_moves {
    int idx;
    char hist[64];
};



static inline void add_move(struct hist_moves *hist, int move) {
    int idx = ++hist->idx;
    //hist->hist[hist->idx/2] |= move << (4*(hist->idx%2));  // too hard/impossible?

    switch (idx % 8) {
        case 0: case 1:
            hist->hist[idx/8*3]   |= move << (5-3*(idx%8));
            break;
        case 2:
            hist->hist[idx/8*3]   |= move >> 1;
            hist->hist[idx/8*3+1] |= move << 7;
            break;
        case 3: case 4:
            hist->hist[idx/8*3+1] |= move << (4-3*((idx%8)-3));
            break;
        case 5:
            hist->hist[idx/8*3+1] |= move >> 2;
            hist->hist[idx/8*3+2] |= move << 6;
            break;
        case 6: case 7:
            hist->hist[idx/8*3+2] |= move << (3-3*((idx%8)-6));
            break;
    }
}


static void print_game(struct game_state* state) {
    // top border
    printf("┌───");
    for (int x=1; x<XDIM; x++) {
        printf("┬───");
    }
    printf("┐\n");

    // main field
    for (int y=YDIM-1; y>=0; y--) {
        for (int x=0; x<XDIM; x++) {
            printf("│ %c ", state->f[y][x]);
        }
        printf("│\n");
    };

    // bottom border
    printf("└───");
    for (int x=1; x<XDIM; x++) {
        printf("┴───");
    }
    printf("┘\n");
}


static int is_full(struct game_state* state) {
    return state->played >= XDIM*YDIM;
}

static int play_move(struct game_state* state, char player, int x) {
    if (x < 0 || x >= XDIM)
        return -1;
    if (is_full(state))
        return -2;
    for (int y=0; y<YDIM; y++) {
        if (state->f[y][x] == ' ') {
            state->f[y][x] = player;
            state->played++;
            return 0;
        }
    }
    return -3;
}


static int play_ceo(struct game_state* state) {
    if (is_full(state)) return -2;
    int x = rand() % XDIM;
    while (play_move(state, 'C', x)) {
        x = (x + 1) % XDIM;
    }
    printf("CEO's playing at %d\n", x);
    return 0;
}


static int get_user_move(void) {
    int input;
    int x;

    input = getchar();
    if (input == EOF) {
        exit(EXIT_FAILURE);
    }

    x = input - '0';
    for (;;) {
        input = getchar();
        if (input == EOF || input == '\n')
            break;
    }

    if (x >= 0 && x < XDIM) {
        return x;
    } else {
        return -1;
    }
}


static int play_user(struct game_state* state) {
    if (is_full(state)) return -2;
    int x = -1;
    while (x<0) {
        printf("Where to play: ");
        x = get_user_move();
    }
    play_move(state, 'x', x);
    add_move(state->hist, x);
    //while (play_move(state, 'x', x)) {
    //    x = x + 1 % XDIM;
    //}
    printf("You are playing at %d\n", x);
    return x;
}


static int count(struct game_state* state, char player) {
    int cnt = 0;
    int maxcnt = 0;

    // columns
    for (int x=0; x<XDIM; x++) {
        cnt = 0;
        for (int y=0; y<YDIM; y++) {
            if (state->f[y][x] == player) {
                cnt++;
                maxcnt = cnt > maxcnt ? cnt : maxcnt;
            } else {
                cnt = 0;
            }
        }
    }

    // rows
    for (int y=0; y<YDIM; y++) {
        cnt = 0;
        for (int x=0; x<XDIM; x++) {
            if (state->f[y][x] == player) {
                cnt++;
                maxcnt = cnt > maxcnt ? cnt : maxcnt;
            } else {
                cnt = 0;
            }
        }
    }

    // diag /
    for (int x=-YDIM+1; x<XDIM; x++) {
        cnt = 0;
        for (int y=0; y<YDIM; y++) {
            if (x+y<0 || x+y>=XDIM) continue;
            //printf("%3d, %3d, %3d\n", x+y, y, x);
            if (state->f[y][x+y] == player) {
                cnt++;
                maxcnt = cnt > maxcnt ? cnt : maxcnt;
            } else {
                cnt = 0;
            }
        }
    }

    // diag \:
    for (int y=0; y<YDIM+XDIM-1; y++) {
        cnt = 0;
        for (int x=0; x<XDIM; x++) {
            if (y-x<0 || y-x>=YDIM) continue;
            //printf("%3d, %3d, %3d\n", x, y-x, y);
            if (state->f[y-x][x] == player) {
                cnt++;
                maxcnt = cnt > maxcnt ? cnt : maxcnt;
            } else {
                cnt = 0;
            }
        }
    }
    return maxcnt;
}


static void clear_state(struct game_state* state) {
    memset(state->f, ' ', sizeof(state->f));
    state->played = 0;
}



void zero_missing(void) {
    puts("CONGRATS! Ticket done :) - but.. have you pushed to prod?!");
}
void one_missing(void) {
    puts("One is missing, almost..");
}
void two_missing(void) {
    puts("Two are missing - c'mon, you can do better!");
}
void three_missing(void) {
    puts("Three are missing, you're too good at being bad :P");
}


int main(int argc, char *argv[]) {
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);

    int score_ceo = 0, score_player = 0;
    char win = 'C';
    int tries = 3;
    int missing = 0;

    struct player_data player = {"\0", zero_missing, one_missing, two_missing, three_missing};
    struct ceo_data win_strings = {"FUriOuS", "AnGryYy", "angry", "alarmed", "pleased"};

    struct hist_moves hist = {.idx = -1};

    struct game_state state;
    state.hist = &hist;


    srand(1337);


    puts("CEOnnect Four\n");
    puts("Can you beat the tipsy CEO and still finish the ticket?\n");

    while (win == 'C' && tries-- > 0) {
        puts("The CEO wants to play!");
        //puts(who[tries]);
        printf("Who is playing? ");
        if (!fgets(player.name, pow(2, 3-tries), stdin)) {
            exit(EXIT_FAILURE);
        }

        clear_state(&state);
        print_game(&state);

        for (int i=0; i<XDIM*YDIM; i++) {
            play_user(&state);
            score_player = count(&state, 'x');
            missing = 4 - score_player;
            if (score_player >= 4) {
                win = 'x';
                break;
            }
            play_ceo(&state);
            score_ceo = count(&state, 'C');
            if (score_ceo >= 4) {
                win = 'C';
                break;
            }
            print_game(&state);
        }
        print_game(&state);
        printf("CEO is >>");
        printf(win_strings.s[score_ceo]);
        printf("<<!\n\n");

        printf("There are %d missing to get 4 for you, %s.\n", missing, player.name);
        (*player.end_fns[missing])();
    }

    printf("CEO isn't in the mood for games!\n");
    print_game(&state);
}
