// Test for conversions from snake_case
class my_user_class {};              // BAD: should be MyUserClass
struct my_data_point {};             // BAD: should be MyDataPoint

int main() {
    int my_integer_value = 5;        // BAD: should be myIntegerValue
    double my_temperature = 98.6;    // BAD: should be myTemperature
    
    const int max_buffer_size = 100; // BAD: should be MAX_BUFFER_SIZE
    const double my_constant = 3.14; // BAD: should be MY_CONSTANT
    
    return 0;
}
