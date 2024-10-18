#include <stdio.h>
#include <stdlib.h>

int *myFunc()
{
    int *x = malloc(sizeof(int)); // Allocate memory for an int
    *x = 15;                      // Assign a value to the allocated memory
    return x;                     // Return the pointer to the allocated memory
}

int main()
{
    int *valOfx = myFunc();  // Call myFunc to get the allocated memory
    printf("%d\n", *valOfx); // Print the value stored in the allocated memory
    return 0;                // Return from main
}