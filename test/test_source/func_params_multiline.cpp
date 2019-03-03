/*
 * Test function prototypes that span multiple lines.
 */
#include <iostream>
#include "test.h"
using namespace std;

/**
 * [myfunc description]
 * @param x   [description]
 * @param y   [description]
 * @param arr [description]
 */
void myfunc(int *x, char &y, bool arr[]);

// This is a comment
void myfunc2(int *x,char &y,bool arr[]);

void otherfunc(int x,
    char y,
    bool z);
// This comment should have a blank line above it.
bool onMoreFun();

int main() {
    return 0;
}

void myfunc(int *x, char &y, bool arr[]) {

}

void myfunc(int x, char y, bool z) {

}