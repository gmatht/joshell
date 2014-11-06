#define _GNU_SOURCE
#define _FILE_OFFSET_BITS 64
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <linux/errno.h>


#define MAX_BLOCKSIZE (1024*1024*16)

//#define SEEK_SIZE (blocksize*9)
//#define SEEK_SIZE (MAX_BLOCKSIZE+blocksize)
//#define SEEK_SIZE (blocksize)

#define NSECS_PER_TEST 10

void die(char* s) {
	fputs(s,stderr);
	fflush(stderr);
	exit(0);
}

double d_clock_gettime() {
	struct timeval t;
	if ( gettimeofday(&t,NULL) != 0 ) {
		die ("Cannot get time!");
	}
	return ( ( t.tv_sec ) + ((double)( t.tv_usec ))/(1000*1000) );
}

long long ll_time() {
	struct timeval t;
	if ( gettimeofday(&t,NULL) != 0 ) {
		die ("Cannot get time!");
	}
	return ( ( t.tv_sec*1000*1000 ) + (t.tv_usec ));
}
	

char* get_buffer() {
	unsigned long long pagesize=getpagesize();
	char *realbuff=malloc(MAX_BLOCKSIZE+pagesize+99);
	return (char*)((((long long)(realbuff)+pagesize-1)/pagesize)*pagesize);
}

void myseek (int fd, off_t pos) {
	off_t ret = lseek(fd,pos,SEEK_SET);
        if ( ret != pos ) {
                die("Cannot seek! \n");
        }
}

void main(int argc, char** argv) {

char *mode="rand";

if (argc<2) {
	fprintf(stderr, "\nUsage: %s /dev/myblockdevice [jump|rand|seq|skip] [offset]\n\n",*argv);

	fprintf(stderr, "Write modes:\n");
	fprintf(stderr, "jump: Jump %d bytes between writes\n",MAX_BLOCKSIZE);
	fprintf(stderr, "rand: write to psuedo-random location between writes\n");
	fprintf(stderr, "seq: sequential write\n");
	fprintf(stderr, "skip: write only small blocks, but skip and increasing amount each time\n\n");

	fprintf(stderr, "The offset is mainly useful if your drive has XP corrections, see e.g.:\n");
	fprintf(stderr, "\thttp://lwn.net/Articles/377895/\n\n");
	fprintf(stderr, "Usually you can leave offset at 0 or a large power of two\n\n");

	fprintf(stderr, "Be warned that this will write to the device.\n");
	fprintf(stderr, "It *should* be a non-destructive write, but make backups. \n");
	fprintf(stderr, "(All warrenties are disclaimed etc.)\n\n");

	die("Needs more arguments\n");
}

if (argc>2) {
	mode=argv[2];
}

int OFFSET=MAX_BLOCKSIZE;
if (argc>3) {
	OFFSET=atoi(argv[3]);
}

printf("Offset %d, mode: %s\n",OFFSET,mode); 

char *buffer=get_buffer();
//int fd = open(argv[1], O_DIRECT | O_LARGEFILE | O_RDWR | O_SYNC);
//int fd = open(argv[1], O_DIRECT | O_LARGEFILE | O_RDWR | O_SYNC);
int fmode = O_LARGEFILE | O_RDWR | O_DIRECT | O_SYNC;
//int fmode = O_LARGEFILE | O_RDWR | O_DIRECT;
int fd = open(argv[1], fmode);
//int fd = open(argv[1], O_LARGEFILE | O_RDWR);
off_t filesize = lseek (fd, 0, SEEK_END);
int blocksize=4096;
//blocksize=1024*1024;
int SEEK_SIZE=blocksize;
//blocksize=256*256*2;

double d_clock_gettime();
off_t pos=OFFSET;
/*+( (random() % (filesize/MAX_BLOCKSIZE)) * MAX_BLOCKSIZE);
off_t pos=OFFSET+( (random() % (filesize/MAX_BLOCKSIZE)) * MAX_BLOCKSIZE);
printf ("startifaddsfsdsfdg from offset %lld\n", (long long) random() % (filesize/MAX_BLOCKSIZE));
printf ("startifaddsfsdsfdg from offset %lld\n", (long long) (filesize/MAX_BLOCKSIZE));

printf ("starting from offset %lld\n", (long long) pos);*/

long long odd_factor=filesize;
while (!(odd_factor & 1)) {
	odd_factor/=2;
}
long long power_of_two_factor=filesize/odd_factor;

printf ("Device size: %lld = %lld * %lld\n", (long long) filesize, odd_factor, power_of_two_factor);





if (strcmp(mode,"jump")==0) {
		SEEK_SIZE=MAX_BLOCKSIZE;
}

while ( SEEK_SIZE <= MAX_BLOCKSIZE && blocksize <= MAX_BLOCKSIZE) {
	int counter = 0;
	long long start = ll_time();
	long long wtime = 0;
	long long wstart;
	//while ( d_clock_gettime() - start < NSECS_PER_TEST ) {
	//while ( (d_clock_gettime() - start < NSECS_PER_TEST) && (d_clock_gettime() - start < 1 || counter < 20 ) ) {
	while ( (ll_time() - start < (NSECS_PER_TEST*1000*1000)) && (ll_time() - start < (1000*1000) || counter < 20 ) ) {
		if ((!(fmode & O_SYNC)) && counter % 8 == 0) {
		long long start = ll_time();
			wstart=ll_time();
			fsync(fd);
			wtime+=ll_time()-wstart;
		}
			fsync(fd);
		int ret;
		if ( (pos+blocksize) > filesize ) {
			pos=OFFSET;
		}
		if (strcmp(mode,"rand")==0) {
			pos=(random() % ((filesize-OFFSET)/blocksize)) * blocksize + OFFSET;
		}

		myseek(fd,pos);
		if ( (ret=read (fd, buffer, blocksize)) != blocksize) {
			fprintf(stderr, "pos: %d+%d, ret %d\n", (int) pos,blocksize, ret);
			die("Read error!\n");
		}
	
		myseek(fd,pos);
		wstart=ll_time();
		if (write (fd, buffer, blocksize) != blocksize) {
			die("Write error!\n");
		}
		wtime+=ll_time()-wstart;
		pos+=SEEK_SIZE;
		counter++;
	}

	wstart=ll_time();
	fsync(fd);
	wtime+=ll_time()-wstart;
	long long tot_time=ll_time() - start;
	//double write_and_read_per_sec=(1000*1000*counter/((double)(tot_time)));
	//double write_minus_read_per_sec=(double)(1000*1000*counter/((double)(wtime-(tot_time-wtime);
	double write_per_sec=(1000*1000*counter/((double)(wtime)));
	double writeMB_per_sec=write_per_sec*blocksize/1024/1024;
	//printf("Block size: %8d  Skip: %8d  Read+Write/sec: %8.3lf Write/sec: %8.3lf Write-Read/sec: %8.3lf \n",blocksize,SEEK_SIZE,  (double)(1000*1000*counter/((double)(tot_time))), (double)(1000*1000*counter/((double)(wtime))), (double)(1000*1000*counter/((double)(wtime-(tot_time-wtime)))) );
	printf("Block size: %8d  Skip: %8d Write/sec: %8.3lf (%8.3lfMB) \n",blocksize,SEEK_SIZE, write_per_sec, writeMB_per_sec);

	if (strcmp(mode,"skip")==0) {
		SEEK_SIZE*=2;
	} else if (strcmp(mode,"seq")==0) {
		blocksize*=2;
		SEEK_SIZE=blocksize;
	} else if (strcmp(mode,"jump")==0) {
		SEEK_SIZE=MAX_BLOCKSIZE;
		blocksize*=2;
	} else if (strcmp(mode,"rand")==0) {
		blocksize*=2;
	} else {
		printf("Unknown mode: %s\n", mode);
		die("");
	}
		
}

close (fd);
}
