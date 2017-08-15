#include <iostream>
using namespace std;

int main() {
	bool isActive = true;

    for (int i = 0; i < 10; i++)
    {
        for (int j = 0; j < 10; j++)
        {
            cout << "hahaha";
        }
    }

    while (isActive)
    {
        isActive = false
        do
        {
        	isActive %= 2;
        }
        while (isActive);
    }

    return 0;
}