#include <stdio.h>
#include <string.h>

#define BUFFERSIZE 10

int main (int argc, char *argv[])
{
    char buffer[BUFFERSIZE];
    int i=0;
    while(fgets(buffer, BUFFERSIZE , stdin) != NULL)
    {
	    i++;
	    if (i>1000000){
		    exit(0);
	    }
    }
    return 0;
}
