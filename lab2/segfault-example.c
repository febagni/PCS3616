#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
  printf("Digite um texto qualquer e pressione Enter ao final:\n");

  char *buf;
  buf = malloc(1024);
  fgets(buf, 1024, stdin);

  printf("Texto digitado foi:\n");
  printf("%s\n", buf);

  return 1;
}
