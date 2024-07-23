#time container=lxc firejail --noprofile --blacklist=/tmp --blacklist=/tmp touch /tmp/t2
sudo apt install libfuse-dev # maybe also: libcfg-dev
wget http://opensource.platon.sk/upload/_projects/00003/libcfg+-0.7.0.tar.gz
tar -xf libcfg+-0.7.0.tar.gz
(cd libcfg+-0.7.0; ./configure; make -j4; sudo make install)
cd fuseflt/
patch -p1 <<EOF
diff --git a/Makefile b/Makefile
index 1fd8832..f21acfe 100644
--- a/Makefile
+++ b/Makefile
@@ -24,7 +24,7 @@ VER := $(shell head -n 1 NEWS | cut -d : -f 1)
 all: fuseflt
 
 fuseflt: fuseflt.c NEWS
-	$(CC) $(shell pkg-config fuse --cflags --libs) $(CFLAGS) -lcfg+ -DVERSION=\"$(VER)\" $< -o $@
+	$(CC) $< $(shell pkg-config fuse --cflags --libs) $(CFLAGS) -lcfg+ -DVERSION=\"$(VER)\" -o $@
EOF 
make -j4
LD_LIBRARY_PATH=/usr/local/lib ./fuseflt 
git clone https://github.com/thkala/fuseflt.git
#echo "#$((lsb_release -d -c | sed s/.*:.// ; echo -n $(arch)) | tr '\n' , ; echo)"
#Ubuntu 22.04.3 LTS,jammy,x86_64
