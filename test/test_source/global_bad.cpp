#include <string>
using namespace std;

// Test struct used to create a global variable.
struct my_struct_type {
	int member1;
	int mem2;
	int mem3;
	my_struct_type(int x, int y, int z) {};
};

// Creating a new type should be fine
using my_233_nums = int;

int MYNUM = 5;
my_struct_type BANANAS(1, 2, 3);
my_233_nums GAJ32lj;

float num1, num2, num3;
auto num4 = 5;

int* ptr1;

int* ptr2 = nullptr;

// Test global variables with different types of initialization.
std::string s1{};
std::string s2("hello");
std::string s3 = "hello";
std::string s4{'a', 'b', 'c'};
char a1[3] = {'a', 'b'};
char& c = a1[0];

int main () {
    // nope.jpg
}
