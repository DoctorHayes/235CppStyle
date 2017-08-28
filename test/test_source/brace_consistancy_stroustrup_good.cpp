/*
 * Using the Stroustrup style consistently.
 * https://en.wikipedia.org/wiki/Indent_style#Variant:_Stroustrup
 */

/**
 * Prototype comment
 */
bool myFunc(int num);

int main () {
	int pointX, pointY;
	int array[] = {pointX, pointY, 0};

	if (pointX) {
		return 0;
	}

	if (pointX == pointY) {
		return 1;
	}

	if ((pointX - pointY) == (pointY - pointX)) {
		return 2;
	}
	else if (myFunc(pointX)) {
		while (!something) {
			// do something
		}
	}

	if (pointX)
		return 3;

	if ((pointX - pointX) == 0 &&
		pointX / 2 == 1) {
		return 4;
	}

	if ((pointX - pointX) == 0 &&
		pointX / 2 == 1)
		return 4;

	return 0;
}

bool myFunc(int num) {
	return num > 2;
}