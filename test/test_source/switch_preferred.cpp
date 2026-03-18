bool isVowel(char c)
{
	return (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u' ||
			c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U');
}

bool isWhitespace(char ch)
{
	if( ch == ' ')
        return true;
    else if( ch == '\t')
        return true;
    else if( ch == '\n')
        return true;
    else if( ch == '\r')
        return true;
    else if( ch == '\f')
        return true;
    else if( ch == '\v')
        return true;
    else
        return false;
}