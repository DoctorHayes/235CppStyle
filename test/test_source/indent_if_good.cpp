#include <iostream>
#include <cassert>
using namespace std;

int main() {
    bool xx = true,
        yy = false;

    if (xx && yy) {

    }

    if (xx || yy) {

    }

    if (!xx) {

    }

    if (1 == 2) {
        assert(1 == 2);
    }

    return 0;
}