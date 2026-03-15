// A comment
// Name

#include <iostream>

void splitFunctionCall(
int a,
		int b)
{
	for (int i = 0;
i < a;
			i++)
	{
		if (i > b &&
i < a)
		{
			std::cout << i << std::endl;
		}
	}
}

int main()
{
	splitFunctionCall(
10,
			5);
	return 0;
}
