/*
 * Using the Allman style consistently.
 * https://en.wikipedia.org/wiki/Indent_style#Allman_style
 */

/**
 * Prototype comment
 */
bool myFunc(int num);

//enum Color {RED, GREEN, BLUE};

int main ()
{
	int x, y;
	int array[] = {x, y};

	if (x)
	{
		return 0;
	}

	if (x == y)
	{
		return 1;
	}

	if ((x - y) == (y - x))
	{
		return 2;
	}
	else if (myFunc(x))
	{
		while (!something)
		{
			// do something
		}
	}

	if (x)
		return 3;

	if ((x - x) == 0 &&
		x / 2 == 1)
	{
		return 4;
	}

	if ((x - x) == 0 &&
		x / 2 == 1)
		return 4;

	return 0;
}

bool myFunc(int num)
{
	return num > 2;
}