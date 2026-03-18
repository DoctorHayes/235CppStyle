bool isVowel(char c)
{
    switch(c) {
        case 'a':
        case 'e':
        case 'i':
        case 'o':
        case 'u':
        case 'A':
        case 'E':
        case 'I':
        case 'O':
        case 'U':
            return true;
        default:
            return false;
    }
}

bool isWhitespace(char ch)
{
    switch (ch) {
        case ' ':
        case '\t':
        case '\n':
        case '\r':
        case '\f':
        case '\v':
            return true;
        default:
            return false;
    }
}

// Two checks are fine
bool isSomething(int c) {
    if (c == 1 || c == 2) {
        return true;
    }
    return false;
}

// Different variables should not trigger
bool diffVars(int a, int b, int c) {
    if (a == 1 && b == 1 && c == 1) {
        return true;
    }
    return false;
}
