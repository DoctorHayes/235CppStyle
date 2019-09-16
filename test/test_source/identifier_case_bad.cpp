const int* ptr = new int();
const int _No_Good;
const int No_Good;
const int Bad;
const double bad;
const string GOOD_GOING;
const int& nop = bad;

const int no_Good99;

const long _i;

const int badArray[10];
const int GOOD_ARRAY[10];
const int badInitializedArray[] = {0, 1, 2};

class GoodClass
{

};

class badClass
{

};

struct badStruct
{

};

struct GoodStruct
{

};

const Class test;

class ForwardDec;

class c_class
{

};

class c
{

};

class _
{

};

struct _badName
{

};

enum badColorType {RED, GREEN, BLUE};

int fun(const int thisIsFine);

int fineFunc(const std::string& goodConstParam);

void test(int NotOkay); // does not test for this yet.

void GoodNamespace::goodFunName(int ok);
void GoodNamespace::BadFunName(int ok);

int main ()
{

	int Bad;
	int Bad_Name;
	int good;
	signed char BAD_SIGNED_CHAR;
	unsigned double BAD_DUB;
	const bool IS_GOOD;
	const int GOOD;
	const short noGood;
	constval test;
	auto Bad_Name2 = 3;
	ifstream BadIStream;
	ofstream BadOStream;
	int bad_1;
	int bad_2;

	string Name;
	const string name;
	const int max = 2;
	const unsigned int seed = static_cast<unsigned int>(time(nullptr));

	const int badArray[10];
	const int badArray2[] = {1, 2, 3, 4};
	int BAD_ARRAY[] = {1, 2, 3, 4};

	return 0;
}

void BadFunc (int goodParam)
{

}

void goodFunc (int BadParam)
{

}