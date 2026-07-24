// Test for conversions from PascalCase
class mySimpleClass {};              // BAD: should be MySimpleClass
struct myDataStructure {};           // BAD: should be MyDataStructure

int main() {
    int MyIntegerValue = 5;          // BAD: should be myIntegerValue
    double MyTemperature = 98.6;     // BAD: should be myTemperature
    
    const int MaxBufferSize = 100;   // BAD: should be MAX_BUFFER_SIZE
    const double MyConstant = 3.14;  // BAD: should be MY_CONSTANT
    
    return 0;
}
