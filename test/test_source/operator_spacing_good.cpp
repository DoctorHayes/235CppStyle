#include <iostream>
using namespace std;

int main() {
    int num = 0;
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
    num--;

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

    if (num < 0)
        return -1;

    strPtr->name;

    static_cast<int>(4.9);
    dynamic_cast<double>(num);

    num = (10 + num)
        * 2;

    cout << ""
        << num << ""
        << num << '.' << endl;

    return 0;
}