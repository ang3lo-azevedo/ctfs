#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>


void init() {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);
  alarm(30);
}

void win() {
  system("cat flag.txt");
}

int main() {
  init();
  float location;
  puts("Let's jump to a new location.");
  printf("Where do you wanna go? ");
  scanf("%f",&location);
  void (*jump)() = (void (*)())*(uintptr_t *)&location;
  printf("Jumping to: %p\n", jump);
  jump();
  return 0;
}