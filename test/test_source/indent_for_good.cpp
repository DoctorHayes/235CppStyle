void sortPhrases(Phrase phrases[], unsigned int arrayLength);

int main()
{
	int sum = 0;

	for (int index = 0; index < 10; index++)
	{
		sum += index;
	}

	return 0;
}

struct Phrase
{
	string phrase;
	int guessesRequired;
};

// Selection Sort
void sortPhrases(Phrase phrases[], unsigned int arrayLength)
{
	unsigned int sortedIndex;
	unsigned int unsortedIndex;
	Phrase tempPhrase;

	// advance the position through the entire array
	for (sortedIndex = 0; sortedIndex < arrayLength - 1; sortedIndex++)
	{
		// find the min element in the unsorted
		//     phrases[sortedIndex ... arrayLength-1]

		// assume the min is the first unsorted element
		unsigned int minIndex = sortedIndex;
		unsigned int minValue = phrases[minIndex].guessesRequired;

		// test against elements after sortedIndex to find the smallest
		for (unsortedIndex = sortedIndex + 1; unsortedIndex < arrayLength;
			unsortedIndex++)
		{
			if (phrases[unsortedIndex].guessesRequired < minValue)
			{
				// found new minimum; remember its index
				minIndex = unsortedIndex;
				minValue = phrases[unsortedIndex].guessesRequired;
			}
		}

		// Move the minimum element to the sorted position
		// If not already the minimum, swap values
		if (minIndex != sortedIndex)
		{
			tempPhrase = phrases[sortedIndex];
			phrases[sortedIndex] = phrases[minIndex];
			phrases[minIndex] = tempPhrase;
		}
	}
}