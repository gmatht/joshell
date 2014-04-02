//#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

//Version 1.0
//Example GolfScratch:
// GA"n="Si"0"Sn["answer"]U=Rn"1"O=\%Rn2"0"Sn+*3Rn1Ci1["say:"Ri]]]'

int needcomma=0;

void comma(){
	if (needcomma) {
		putchar(',');
		putchar(' ');
	} else {
		needcomma=1;
	}
}

int readop();
/*
void read_param(){
	int c=getchar();
	putchar(c);

	comma();
	
	if (isdigit(c)){
		while ((c=getchar())!=' ') { putchar(c); };
		ungetc(c,stdin);
	} else {
		switch(c){
			//case '"': while (!strchr("\"\\",c=getchar())) {putchar(c)}; break;
			case '"': while ((c=getchar())!='"') {
				putchar(c);
			        if (c='\\') {putchar(getchar());}
			}; break;
			case '[': needcomma=0; putchar('['); readop(); putchar(']'); needcomma=1; break;
			otherwise: puts("\nPARSE ERROR HERE! (Parameter Expected)\n");
		}
	}
}*/

void printop(int i, char *op) {
        putchar('[');
//	if (op==NULL) {
//		needcomma=0;
//	} else {
		printf("\"%s\"", op);
		needcomma=1;
//	}
	//while(i>0){read_param();i--;};
	while(i>0){readop();i--;};
        putchar(']');
	needcomma=1;
}
int readop(){
int c=0;
while(strchr(" \n\t",c=getchar())){}
if(c==EOF) {
	//puts("EOF\n");
	return(0);
}
if (c!=']') comma();
if (isdigit(c)){
	putchar(c);
	while (isdigit(c=getchar())) { if (c==EOF){return;}; putchar(c); };
	ungetc(c,stdin);
} else { if (islower(c)) {
	printf("\"%c\"", c);
}
switch (c){
	case 'A': printop(1,"doAsk"); break;
	case 'C': printop(2,"changeVar:by:"); break;
	case 'G': printop(0,"whenGreenFlag"); break;
	case 'O': printop(2,"doIfElse"); break; //otherwise
	case 'S': printop(2,"setVar:to:"); break;
	case 'R': printop(1,"readVariable"); break;
	case 'U': printop(2,"doUntil"); break;
	case '*': printop(2,"*"); break;
	case '-': printop(2,"-"); break;
	case '/': printop(2,"/"); break;
	case '+': printop(2,"+"); break;
	case '=': printop(2,"="); break;
	case '&': printop(2,"&"); break;
	case '\%': printop(2,"\%"); break;
	case '"': putchar(c);while ((c=getchar())!='"') {
			if (c==EOF){return(0);};
			putchar(c);
			//puts("GOO\n");
			if (c=='\\') {putchar(getchar());}
		  }; 
		  putchar(c);
		break;
	case 'M': printop(2,"\\/"); break; //Modulus?
	//case '[': printop(getchar()-'0',NULL); break;
	case ']': putchar(c);needcomma=1; return (0); break;
	case '[': putchar(c);needcomma=0; while(readop()); return(1); break;
	otherwise: printf("\nPARSE ERROR HERE! (Operator Expected)\n");
}
}
return(1);}

void main() {while(readop()){}}
