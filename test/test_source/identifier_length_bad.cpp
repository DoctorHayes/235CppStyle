for (int i = 0; i < 2; ++i)
		cout << i << endl;
int prototype(double foo, long int *h);
int p(string& str);
const int C;
int g;

int main ()
{
	double x, y, z;
	int a[];
	bool d;
	int* p = nullptr;

	char c='c'; // this error will be detected after spacing is fixed;
	int val = x; // x is bad, but the error goes with the declaration.

	int z
	;

	return 0;
}

void definition(int *a, short*b, string* c, float& d, bool &e)
{
	int good;
}