// Edge cases and additional test cases

// Multiple variables on different lines
class UserAccount {};    // GOOD: PascalCase
class productHandler {}; // BAD: starts with lowercase

struct Node {};      // GOOD: PascalCase
struct leaf_node {}; // BAD: uses underscores

#define PREPROCESSOR_DEFINE

// Const with unsigned types
int main() {
  const unsigned int SEED = 42;     // GOOD: UPPER_SNAKE_CASE
  const unsigned int seed = 42;     // BAD: camelCase
  const signed int ERROR_CODE = -1; // GOOD: UPPER_SNAKE_CASE
  const signed int errorCode = -1;  // BAD: camelCase

  // Pointer types
  int *somePointer = nullptr; // GOOD: camelCase
  int *SomePointer = nullptr; // BAD: PascalCase

  // BAD: technically, a non-const pointer to constant int, but we'll treat it
  // as a constant.
  const int *constantPtr = nullptr;
  const int *ConstantPtr = nullptr; // BAD: PascalCase

  // Reference types
  int &someReference = somePointer[0]; // GOOD: camelCase
  int &SomeReference = somePointer[0]; // BAD: PascalCase

  // Arrays
  int dataArray[10];             // GOOD: camelCase
  int DataArray[10];             // BAD: PascalCase
  const int MAX_ARRAY_SIZE = 10; // GOOD: UPPER_SNAKE_CASE
  const int maxArraySize = 10;   // BAD: camelCase

  return 0;
}
