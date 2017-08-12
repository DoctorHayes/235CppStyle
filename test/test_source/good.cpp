/*
 * good.cpp
 *
 * First Last
 * uniqname@umich.edu
 *
 * A sample file for CSCI 235 Style Grader.
 *
 * Demonstrates good style.
 */

#include <iostream>
using namespace std;

/**
 * Requires: Nothing.
 * Modifies: stdout.
 * Effects:  Greets the world.
 */
void greet(void);

int main(int argc, const char * argv[])
{
    // greet the user
    greet();
    cout << "bye.\'" << '*' << '\\' << '\"' << '\'*' << '-' << '+' << endl;
    int val;
    cin >> val;

    return 0;
}

void greet(void)
{
    cout << "o hai world!" << endl;
    cout << "o hai world!" << endl;
}
