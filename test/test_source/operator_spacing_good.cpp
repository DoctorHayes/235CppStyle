#include <iostream>
using namespace std;

int main() {
    int x = 0;
    // check compound operators
    x += 1;
    x *= 1;
    x /= 1;
    x %= 2;
    x != 1;
    x == 1;
    x >= 2;
    x <= 2;
    x && false;
    x || true;

    // increment/decrement operators
    x++;
    x--;

    // normal operators
    x + 1;
    x - 1;
    x * 2;
    x / 1;
    x % 2;
    x > 1;
    x < 1;
    x = 1;
    !x;
    -x;
    +x;
    (-x);
    1 + -x;
    x - -x;
    x && -x
    x = -x;
    x /= -x;

    if (x < 0)
        return -1;

    strPtr->name;

    static_cast<int>(4.9);
    dynamic_cast<double>(x);

    x = (10 + x)
        * 2;

    return 0;
}