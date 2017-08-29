#include <iostream>
using namespace std;

int main() {
    int x = 0;
    // check compound operators
    x+=1;
    x*=1;
    x/=1;
    x%=2;
    x!=1;
    x==1;
    x>=2;
    x<=2;
    x&&false;
    x||true;

    // increment/decrement operators
    x++; // valid
    x--; // valid
    ++x; // valid
    --x; // valid

    // normal operators
    x+1;
    x +1;
    x+ 1;
    x-1;
    x*2;
    x/1;
    x%2;
    x>1;
    x<1;
    x=1;
    !x; // valid
    ! x;
    -x; // valid
    - x;
    +x; // valid
    (+ x);

    if (dynamic_cast<double>(x)< 2.0)
        x += 2; // valid

    return 0;
}