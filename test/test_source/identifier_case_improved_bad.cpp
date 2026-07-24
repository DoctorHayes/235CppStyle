// Test cases for incorrectly named identifiers

// Classes should be PascalCase (not camelCase or snake_case)
class myClass {};          // WRONG: starts with lowercase
class my_class {};         // WRONG: uses underscores
struct myStruct {};        // WRONG: starts with lowercase
struct my_struct {};       // WRONG: uses underscores
enum badColorType {};      // WRONG: mixed case
enum bad_color_type {};    // WRONG: snake_case

int main() {
    // Non-const variables should be camelCase (not PascalCase or snake_case)
    int MyVariable = 5;         // WRONG: PascalCase
    int my_variable = 5;        // WRONG: snake_case
    double Temperature = 98.6;  // WRONG: PascalCase
    double temp_value = 98.6;   // WRONG: snake_case
    
    // Const variables should be UPPER_SNAKE_CASE (not camelCase or PascalCase)
    const int maxSize = 100;          // WRONG: camelCase
    const int MAX_size = 100;         // WRONG: mixed case
    const int MaxSize = 100;          // WRONG: PascalCase
    const double pi = 3.14159;        // WRONG: camelCase
    
    constexpr int bufferSize = 256;   // WRONG: camelCase
    constexpr double GOLDEN_ratio = 1.618; // WRONG: mixed case
    
    return 0;
}
