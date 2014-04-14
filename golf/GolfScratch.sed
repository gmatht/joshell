s/"doAsk"/A/g
s/"changeVar:by:"/C/g
s/"whenGreenFlag"); break;
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
	case 'M': printop(2,"\\/"); break; //Modulus?
	case '0': printop(0,NULL); break;
	case '1': printop(1,NULL); break;
	case '2': printop(2,NULL); break;
	case '3': printop(3,NULL); break;
	otherwise: printf("\nPARSE ERROR HERE! (Operator Expected)\n");
}
}

void main() {readop();}
s/"doAsk"/A/g
s/"changeVar:by:"/C/g
s/"whenGreenFlag/G/g
s,"doIfElse",O,g
s,"setVar:to:",S,g
s,"readVariable",R,g
s,"doUntil",U,g
s,"*",*,g
s,"-",-,g
s,"-",/,g
s,"+",+,g
s,"=",=,g
s,"&",&,g
s,"%",%,g
s,"\\/",M,g
	case '0': printop(0,NULL); break;
	case '1': printop(1,NULL); break;
	case '2': printop(2,NULL); break;
	case '3': printop(3,NULL); break;
	otherwise: printf("\nPARSE ERROR HERE! (Operator Expected)\n");
}
}

void main() {readop();}
