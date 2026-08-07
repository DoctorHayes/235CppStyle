// Test cases for correctly named identifiers
#include <string>
using namespace std;

// Classes and structs should be PascalCase
class MyClass {};
struct MyStruct {};
class Student {};
struct DataPoint {};

enum Color { RED, GREEN, BLUE };
enum ErrorCode { SUCCESS, ERROR, FAILED };

// Non-const variables should be camelCase
int main() {
    int myVariable = 5;
    double temperature = 98.6;
    string studentName = "John";
    bool isValid = true;
    
    // Function parameters in camelCase
    auto calculateSum = [](int value1, int value2) { return value1 + value2; };
    
    // Const variables should be UPPER_SNAKE_CASE
    const int MAX_SIZE = 100;
    const double PI = 3.14159;
    const string DEFAULT_NAME = "Unknown";
    
    // Const expressions
    constexpr int BUFFER_SIZE = 256;
    constexpr double GOLDEN_RATIO = 1.618;

    constexpr string_view VOWELS {"aeiouAEIOU"}; // all of the vowels.
    
    return 0;
}
