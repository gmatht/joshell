//#define n_edges 17
#include <stdlib.h>
#include <stdio.h>

//Finds a 4-colouring of edges in a  graph with 17 vertices without any monochromatic triangles
//Easy to change # colours and number of vertices

void main() {
int g[17][17];
int ok=0;
int i,j,k;
int loops=0, changes=0;

for(i=0;i<17;i++){
	for(j=0;j<17;j++){
		g[i][j]=0;
	}
}

while (!ok){
ok=1;
loops++;
puts("\n--\n");
for(k=0;k<17;k++){
	for(j=0;j<k;j++){
		for(i=0;i<j;i++){
			int c=g[i][j];
			if ((c == g[j][k]) && c==g[i][k]){
				//int r=rand()%3;
				int new_c=rand()%4;
				changes++;
				ok=0;
				if (rand()%2) {
					g[j][k]=new_c;
					printf("%2d->%2d: %c\n",j,k,(new_c+'a'));
				} else {
					g[i][k]=new_c;
					printf("%2d->%2d: %c\n",i,k,(new_c+'a'));
				}
			}
		}
	}
}
}

printf("Loops: %d, changes: %d \n",loops,changes);


puts("\n\n-- Final Graph --\n");
printf("   ");
for(j=0;j<17;j++){
	printf("%2d ",j);
}
	
for(i=0;i<17;i++){
	printf("\n\n%2d   ",i);
	for(j=0;j<i;j++){
		printf("%c  ",(g[j][i]+'a'));
	}
}


}
