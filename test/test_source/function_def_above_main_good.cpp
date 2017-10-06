#include <string>
using namespace std;

//void myFn(void) {}

MyStruct my_Function(Garbage &stuff);

SecondStruct_Erbla thisfn(int, bool, int);

int* thisFun2();

*int* testFunction(int** test);

std::string twoLinePrototype (const std::string& currentPhrase,
	std::string correctLetters);

int* threeLinePrototype (const int& num,
	std::string num2,
	Garbage* pointPointer1);

//loads phrases into vector from file
bool loadPhrasesFromFile(std::vector<PHRASE>& phrases, std::string fileName);

/*
 * This function takes the user's name as a parameter and displays a greeting
 * with that name.
 */
void greet(const string& userName = "Earthling");

#include <iostream>

int  main()
{

}


std::string twoLinePrototype (const std::string& currentPhrase,
	std::string correctLetters);
{
	// good definition
	return "";
}

void greet(const string& userName)
{
	// Display a greeting with the user's name
	cout << "Greetings " << userName << "!" << endl;
}