//#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

//Version 0.12
//Example GolfScratch:
// GA"n="Si"0"Sn["answer"]U=Rn"1"[O=\%Rn2"0"Sn+*3Rn1Ci1]["say:"Ri]

// :w|!gcc % 2>&1|head&&echo 'GA"n="Si0Sn["answer"]U=Rn"1"[O=\%Rn2"0"[SnMRn2][Sn+*3Rn1]Ci1] ["say:"Ri]'|./a.out>out

int needcomma=0;
int suppress_newlines=0;

void comma(){
	if (needcomma) {
		putchar(',');
		if (suppress_newlines) {
			putchar(' ');
		} else {
			putchar('\n');
		}
	} else {
		needcomma=1;
	};
	//suppress_next_newline=suppress_newlines;
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

void printop(int i, int loop, char *op) {
	int old_sn=suppress_newlines;
        putchar('[');
//	if (op==NULL) {
//		needcomma=0;
//	} else {
	printf("\"%s\"", op);
	needcomma=1;

	suppress_newlines=!loop;
	//	suppress_next_newline=!loop;
//	}
	//while(i>0){read_param();i--;};
	while(i>0){if(loop)suppress_newlines=0;loop;readop();i--;};
        putchar(']');
	needcomma=1;
	suppress_newlines=old_sn;
}
int readop(){
int old_sn=suppress_newlines;
int c=0;
while(c=getchar()){if (c==EOF||!strchr(" \n\t",c)) break;}
if(c==EOF||c==']') {
	//puts("EOF\n");
	return(0);
}
comma();
if (isdigit(c)){
	putchar(c);
	while (isdigit(c=getchar())) { if (c==EOF){return 0;}; putchar(c); };
	ungetc(c,stdin);
	return 1;
} else { if (islower(c)) {
	printf("\"%c\"", c);
}
switch (c){
	case 'A': printop(1,0,"doAsk"); break;
	case 'C': printop(2,0,"changeVar:by:"); break;
	case 'G': printop(0,0,"whenGreenFlag"); break;
	case 'M': printop(2,0,"\\/"); break; //Modulus?
	case 'O': printop(3,1,"doIfElse"); break; //otherwise
	case 'S': printop(2,0,"setVar:to:"); break;
	case 'R': printop(1,0,"readVariable"); break;
	case 'U': printop(2,1,"doUntil"); break;
	case '*': printop(2,0,"*"); break;
	case '-': printop(2,0,"-"); break;
	case '/': printop(2,0,"/"); break;
	case '+': printop(2,0,"+"); break;
	case '=': printop(2,0,"="); break;
	case '&': printop(2,0,"&"); break;
	case '\%': printop(2,0,"\%"); break;
	case '"':  suppress_newlines=1;
		   putchar(c);while ((c=getchar())!='"') {
			if (c==EOF){return(0);};
			putchar(c);
			//puts("GOO\n");
			if (c=='\\') {putchar(getchar());}
		  }; 
		  putchar(c);
		break;
	//case '[': printop(getchar()-'0',NULL); break;
	//case ']': putchar(c);needcomma=1; return (0); break;
	case '[': //suppress_newlines=1;
		  putchar(c);needcomma=0; while(readop()){};
		  putchar(']');needcomma=1;
		  //suppress_newlines=old_sn;
		  break;
	otherwise: printf("\nPARSE ERROR HERE! (Operator Expected)\n");
}
}
return(1);}

void main() {while(readop()){}}
