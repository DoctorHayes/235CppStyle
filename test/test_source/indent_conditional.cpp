#include <iostream>
using namespace std;

int main() {
    int xx;
    int array[4][3] = {
        // {1, 2, 3},
        // {4, 5, 6},
        // {7, 8, 9},
        {
            10, 11, 12
        }
    };
    cout << "Hello world";

bool y = true;
        xx++;
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
            xx++;
        } else {
            if (true) {

            }
            else if (y) {xx--;}
        }
    }

    if (xx)
        cout << "Hahah";
    if (xx) cout << "Shouldn't be an issue";

    int zzz = 0;

    if (xx == 2 ||
        xx == 3)
        cout << "Multi-line conditional statements should be fine." << endl;

    cout << "This is ok"
        << "This is okay to."
        << (2 + 4)
        << endl;

    return 0;
}