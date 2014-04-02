int needcomma=0;

void comma(){
	if (needcomma) {
		puts(', ');
	} else {
		needcomma=1;
	}
}

void read_param(){
	int c=getch();
	putc(c);

	comma();
	
	if (isdigit(c)){
		while ((c=getch())!=' ') { putc(c); };
		ungetc(c);
	} else {
		switch(c){
			//case '"': while (!strchr("\"\\",c=getch())) {putc(c)}; break;
			case '"': while ((c=getch())!='"') {
				putc(c)
			        if (c='\') {putc(getch())}
			}; break;
			case '[': needcomma=0; readop();  break;
			otherwise: puts("\nPARSE ERROR HERE! (Parameter Expected)\n");
		}
	}
}

void printop(int i, char *op) {
	comma();
        putc('[');
	if (op==NULL) {
		needcomma=0;
	} else {
		printf("\"%s\"", op);
		needcomma=1;
	}
	while(i>0){read_param();i--;};
        putc(']');
	needcomma=1;
}
		
void readop(){
int c;

while((c=getch())==' '){}
switch (c){
	case 'A': printop(1,"doAsk"); break;
	case 'C': printop(2,"changeVar:by:"); break;
	case 'G': printop(0,"whenGreenFlag"); break;
	case 'O': printop(2,"doIfElse"); break; //otherwise
	case 'S': printop(2,"setVar:to:"); break;
	case 'R': printop(2,"readVariable"); break;
	case 'U': printop(2,"doUntil"); break;
	case '*': printop(2,"*"); break;
	case '-': printop(2,"-"); break;
	case '/': printop(2,"-"); break;
	case '+': printop(2,"+"); break;
	case '=': printop(2,"="); break;
	case '&': printop(2,"&"); break;
	case '%': printop(2,"%"); break;
	case 'M': printop(2,"\/"); break; //Modulus?
	case '0': printop(0,NULL); break;
	case '1': printop(1,NULL); break;
	case '2': printop(2,NULL); break;
	case '3': printop(3,NULL); break;
	otherwise: printf("\nPARSE ERROR HERE! (Operator Expected)\n");
}
}

void main() {readop();}
