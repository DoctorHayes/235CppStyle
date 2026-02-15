/*
 * cin_cout_newline_good.cpp
 *
 * Test file for cin/cout newline check - GOOD examples
 * Newlines should appear AFTER cin, not in the prompt
 */

#include <iostream>
using namespace std;

int main()
{
    int num;
    double value;
    string name;

    // GOOD: Newline after cin
    cout << "Enter a number: ";
    cin >> num;
    cout << endl;

    // GOOD: Multiple prompts with proper newline placement
    cout << "Enter your name: ";
    cin >> name;
    cout << endl;

    cout << "Enter a value: ";
    cin >> value;
    cout << endl;

    // GOOD: Prompt without any newline at all
    cout << "Another number: ";
    cin >> num;

    // GOOD: Output after cin without prompt
    cin >> value;
    cout << "You entered " << value << ".\n";

    // GOOD: Newline after cin
    cout << "Welcome to the program!\nEnter a number: ";
    cin >> num;
    cout << endl;

    return 0;
}
