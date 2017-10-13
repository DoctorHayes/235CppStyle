#include <iostream>
using namespace std;

int main() {
    int num = 0;

    // check compound operators
    num+=1;
    num*=1;
    num/=1;
    num%=2;
    num!=1;
    num==1;
    num>=2;
    num<=2;
    num&&false;
    num||true;
    num<<2;
    num>>2;

    // increment/decrement operators
    num++; // valid
    num--; // valid
    ++num; // valid
    --num; // valid

    // normal operators
    num+1;
    num +1;
    num+ 1;
    num-1;
    num*2;
    num/1;
    num%2;
    num>1;
    num<1;
    num=1;
    !num; // valid
    ! num;
    -num; // valid
    - num;
    +num; // valid
    (+ num);

    if (dynamic_cast<double>(num)< 2.0)
        num += 2; // valid

    // Mistake on last line
    cout << ""          // valid
        << num << ""    // valid
        << num << '.' <<endl; // 1 bad spacing

    switch(num % 2)
    {
        case 0:
            cout << "even";
            break;
        case 1:
        case - 1: // bad
            cout << "odd";
    }

    return 0;
}