void fun() {
  // Bad: technically, non-const pointer to constant int
  const int *ptr = new int();

  const int _No_Good;      // Bad
  const int No_Good;       // Bad
  const int Bad;           // Bad
  const double bad;        // Bad
  const string GOOD_GOING; // Good
  const int &nop = bad;    // Bad

  const int no_Good99; // Bad

  const long _i; // Bad

  const int badArray[10];                      // Bad
  const int GOOD_ARRAY[10];                    // Good
  const int badInitializedArray[] = {0, 1, 2}; // Bad
}

class GoodClass // Good
{};

class badClass // Bad
{};

struct badStruct // Bad
{};

struct GoodStruct {};

const Class test; // Bad

class ForwardDec; // Good

class c_class // Bad
{};

class c // Bad
{};

class _ // Bad
{};

struct _badName // Bad
{};

enum badColorType { RED, GREEN, BLUE }; // Bad Enum type name

int fun(const int thisIsNotFine); // Bad
int fineFuncBad(const std::string &badConstParam); // Bad

void test(int NotOkay); // Bad: does not test for this yet.

void GoodNamespace::goodFunName(int ok); // Good
void GoodNamespace::BadFunName(int ok);  // Bad

int main() {
  constexpr int bAD_BUT_MOSTLY_Good{2}; // Bad
  int Bad;                              // Bad
  int Bad_Name;                         // Bad
  int good;                             // Good
  signed char BAD_SIGNED_CHAR;          // Bad
  unsigned double BAD_DUB;              // Bad
  const bool IS_GOOD;                   // Good
  const int GOOD;                       // Good
  const short noGood;                   // Bad
  constval test;       // Good: Custom type with "const" in the name
  auto Bad_Name2 = 3;  // Bad
  ifstream BadIStream; // Bad
  ofstream BadOStream; // Bad
  int bad_1;           // Bad
  int bad_2;           // Bad
  double bad_name;     // Bad
  double bad_Name;     // Bad

  string Name;                                                        // Bad
  const string name;                                                  // Bad
  const int max = 2;                                                  // Bad
  const unsigned int seed = static_cast<unsigned int>(time(nullptr)); // Bad
  const unsigned int ARRAY_LENGTH = 62;                               // Good

  const int badArray[10];               // Bad
  const int badArray2[] = {1, 2, 3, 4}; // Bad
  int BAD_ARRAY[] = {1, 2, 3, 4};       // Bad

  constexpr int BadConstExpr = 5;     // Bad
  constexpr int GOOD_CONST_EXPR = 10; // Good

  return 0;
}

void BadFunc(int goodParam) // Bad function name
{}

void goodFunc(int BadParam) // Bad parameter name
{}