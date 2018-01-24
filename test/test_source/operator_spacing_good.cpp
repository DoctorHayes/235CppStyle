#include <iostream>
using namespace std;

int main() {
    int num = 0;

    // Check floating-point notation
    5.0279e-31;
    1.020E+003;
    5.e-31;

    // check compound operators
    num += 1;
    num *= 1;
    num /= 1;
    num %= 2;
    num != 1;
    num == 1;
    num >= 2;
    num <= 2;
    num && false;
    num || true;

    // increment/decrement operators
    num++;
    ++num;
    num--;
    --num;

    // normal operators
    num + 1;
    num - 1;
    num * 2;
    num / 1;
    num % 2;
    num > 1;
    num < 1;
    num = 1;
    !num;
    -num;
    +num;
    (-num);
    1 + -num;
    num - -num;
    num && -num
    num = -num;
    num /= -num;
    num % +2;

    if (num < 0)
        return -1;

    strPtr->name;

    static_cast<int>(4.9);
    dynamic_cast<double>(num);
    static_cast<std::string>("test");

    num = (10 + num)
        * 2;

    cout << ""
        << num << ""
        << num << '.' << endl;

    switch(num % 2)
    {
        case 0:
            cout << "even";
            break;
        case 1:
        case -1: // good
            cout << "odd";
    }

    return 0;
}