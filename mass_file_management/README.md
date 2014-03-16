Mass File Management
=======

I have many different disks (primarily harddisks) storing various files. I want to know that they are all backed up in some form. Given that I have terrabytes of files somehow (backups of backups apparently) I don't want to just backup everything onto new media yet again.  I'd like a utility that allows me to copy all files on X that do not yet exist on Y to Y. Other useful things would be:

1) To list all files on X that are not duplicated/backed up on other media
2) Deduplicate files on X
3) To list all files that are not duplicated onto offline or WORM storage
4) To list all files that are not duplicated onto offsite storage
5) Store computed hashes for re-use

## Other programs

### rsync
Rsync would be great if all my files shared the same directory structure. As they do not, it is not a complete solution.

### du 
The du command is quite handy. With the -ab option you get precise byte counts for each file, which can be quite handy for quickly guessing whether two files are duplicates.

### hashdeep
A handy set of commands for creating hashes of files. I find 
     sha256deep -reztcl
the most useful. hashdeep clearly isn't as fast as du, and unfortunately sha256deep normalises dates to GMT whereas du doesn't, making comparing timestamps less trivial.
Hashdeep doesn't have a inbuilt way of quickly recomputing hashes for changed files only, nor an option to restart interrupted runs.

### bedup
btrfs has handy deduplication facilities. One possible approach is just to copy everything onto a large btrfs drive and the deduplicate the files
  https://github.com/g2p/bedup/blob/master/README.rst

There are many other deduplication utilities.
	rdfind: http://rdfind.pauldreik.se/
	duff:   http://duff.dreda.org/

However they seem to be all limited in two ways:
1) they don't store hashes for later reuse, resulting in slow performance on huge volumes
2) it is hard to ask them to list the files that do *not* exist on my archive. 
