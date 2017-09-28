#include <iostream>
using namespace std;

int main() {
    int x;
    int array[3][3] = {
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9},
        {
            10, 11, 12
        }
    };
    cout << "Hello world";

bool y = true;
        x++;
    if (y) {
        cout << "Yes";
    }
    else if (y) {
            cout << "Bwahaha";
    }
    else {
    cout << "hbiufpdsa";
    }

    if (true) {
        if (false) {
            x++;
        } else {
            if (true) {

            }
            else if (y) {x--;}
        }
    }

    if (x)
        cout << "Hahah";
    if (x) cout << "Shouldn't be an issue";

    int z = 0;

    if (x == 2 ||
        x == 3)
        cout << "Multi-line conditional statements should be fine." << endl;

    cout << "This is ok"
        << "This is okay to."
        << (2 + 4)
        << endl;

    return 0;
}