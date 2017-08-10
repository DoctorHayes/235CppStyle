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

int  main()
{

}


std::string twoLinePrototype (const std::string& currentPhrase,
	std::string correctLetters);
{
	// good definition
	return "";
}