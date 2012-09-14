#include <stdio.h>
#include <stdlib.h>
int main()
{
    const int N = 100;
    int a[N];
    int i;
    char buffer[50];

    for(i = 1; i <= N; i++)
    {
        if (i % 3 == 0) {
            printf("Fizz");
        }
        if (i % 5 == 0) {
            printf("Buzz");
        }
        if (i % 3 != 0 && i % 5 != 0) {
            sprintf(buffer, "%d", i);
            printf(buffer);
        }
        printf("\n");
    }
}
