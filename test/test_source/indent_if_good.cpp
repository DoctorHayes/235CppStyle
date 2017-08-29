#include <iostream>
#include <cassert>
using namespace std;

int main() {
    bool x = true,
        y = false;

    if (x && y) {

    }

    if (x || y) {

    }

    if (!x) {

    }

    if (1 == 2) {
        assert(1 == 2);
    }

    return 0;
}