/*
 * cin_cout_newline_bad.cpp
 *
 * Test file for cin/cout newline check - BAD examples
 * These should trigger errors because newlines are in prompts before cin
 */

#include <iostream>
#include <string>
using namespace std;

int main()
{
    int num;
    double value;
    string name;

    // BAD: Newline in prompt, not after cin (error 1)
    cout << "Enter a number: \n";
    cin >> num;

    // BAD: Using endl in prompt (error 2)
    cout << "Enter your name: " << endl;
    cin >> name;

    // BAD: Escaped newline in prompt (error 3)
    cout << "Enter a value: \n";
    cin >> value;

    // BAD: Multiple stream insertions with endl (error 4)
    cout << "Another number: " << endl;
    cin >> num;

    // BAD: Character literal newlines ('\n') (error 5)
    cout << "Enter a value: " << '\n';
    cin >> value;

    // BAD: Using getline with newline in prompt (error 6)
    cout << "Enter your name: \n";
    getline(cin, name);

    // BAD: Using endl in prompt with getline (error 7)
	cout << "What is your name? \n";
	getline(cin, name);
    cout << endl;

    // BAD: Newline in prompt even with newline after (error 8)
    cout << "Enter another number: \n";
    cin >> num;
    cout << endl;

    return 0;
}
