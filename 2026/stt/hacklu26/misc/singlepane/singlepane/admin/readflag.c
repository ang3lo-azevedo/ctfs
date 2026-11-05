#include <stdio.h>

int main(void)
{
	char buf[256];
	FILE *f = fopen("/flag", "r");

	if (f == NULL) {
		perror("readflag");
		return 1;
	}
	while (fgets(buf, sizeof buf, f) != NULL)
		fputs(buf, stdout);
	fclose(f);
	return 0;
}
