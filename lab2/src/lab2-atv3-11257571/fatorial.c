#include <stdio.h>

int fatorial(int n);

/**
 * Ponto de entrada do programa (entry point).
 */
int main(int argc, char** argv) {
  int n;
  scanf("%d", &n);

  printf("%d\n", fatorial(n));

  return 0;
}

/**
 * Calcula o fatorial do número recebido e retorna o resultado.
 */
int fatorial(int n) {
  return (n==0) ? 1: (n*fatorial(n-1));
}
