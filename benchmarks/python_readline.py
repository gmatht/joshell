#filters output
import subprocess
proc = subprocess.Popen(['yes'],stdout=subprocess.PIPE)
for i in range(0,1000000):
  line = proc.stdout.readline()
