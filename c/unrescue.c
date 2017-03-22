/* Filters a block device or image file based on an ddrescue file,
 * and pipes it to stdout  (zerofilling the missing blocks) 
 * example of use: 
     gcc unrescue.c -o unrescue && sudo partclone.ext4 -D -s /tmp/foo.img -L /tmp/junk -o - | grep ^0x.*0x | ./unrescue 3< /tmp/foo.img > /tmp/foo.new.img ; fsck /tmp/foo.new.img
 */

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>

#define BUFFER_SIZE 0x1000000
char buffer[BUFFER_SIZE];
char zero[BUFFER_SIZE];

long long min(long long x, long long y) {
    if (x<y) return x; else return y;
}

void die(char* s) {
    fprintf(stderr,"FAILED due to %s!\n",s);
    fflush(stderr);
    exit(1);
}

int main() {
  long long pos, size=0, at = 0;
  int i;
  char c;
  int dev=3;
  memset(&buffer, 0, BUFFER_SIZE);
  while (getchar() != EOF) {  
    getchar();
    i=scanf("%llx  %llx  %c\n",&pos,&size,&c);
    fprintf(stderr, "pos= %llx, size = %llx, char = %c\n",pos,size,c);
    if (c=='?') continue;
    if (c!='+') die("c");
    while (at<pos) {
      long long bytes = fwrite(&zero, 1, min(BUFFER_SIZE,(pos-at)), stdout);
      if (!bytes) die("write zeros");
      at+=bytes;
    }
    at=lseek(dev, pos, SEEK_SET);
    if (at!=pos) die("lseek");
    long long remaining=size;
    while (remaining > 0) {
      int m=min(remaining,BUFFER_SIZE);
      long long bytes_read = read(dev, &buffer, m);
      if (!bytes_read) die("read");
      if (bytes_read > remaining) die("read>remaining");
      if (fwrite(&buffer, bytes_read, 1, stdout) != 1) die("write");
      remaining -= bytes_read;
      fprintf(stderr, "read= %llx, remaining = %llx\n",bytes_read,remaining);
    }
    at+=size;
    if (i!=3) die("i!=3");
    //printf("pos= %d\n",i);
    //printf("pos= %llx\n",pos);
  }
  if (c=='?') while(size>0) {
    size--;
    putc(0,stdout);
  }
  fprintf(stderr, "Might have worked, but untested, so may have eaten your data and possibly your dog\n");
  return 0;
}
