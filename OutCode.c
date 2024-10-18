#include <stdio.h>
#include <stdlib.h>

// Iterative Fibonacci function for better performance
int fibonacci(int n) {
    if (n <= 1) {
        return n;
    }

    int a = 0, b = 1, next;
    for (int i = 2; i <= n; i++) {
        next = a + b;
        a = b;
        b = next;
    }
    return b;
}

int main() {
    int random = 5;
    int num = 10;
    
    // Dynamically allocate memory for n and x
    int *n = (int *)malloc(sizeof(int));
    int *x = (int *)malloc(sizeof(int));

    // Check if memory allocation was successful
    if (n == NULL || x == NULL) {
        printf("Memory allocation failed!\n");
        return 1;
    }
    
    *x = random;
    *n = num;

    printf("Fibonacci sequence up to %d:\n", *n);
    
    for (int i = 0; i < *n; i++) {
        printf("%d\n", fibonacci(i));
    }

    // Free dynamically allocated memory at the end
    free(x);
    free(n);

    return 0;
}
