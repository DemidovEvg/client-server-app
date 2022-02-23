import subprocess
import locale

args = ['ping', 'youtube.com']
encoding = locale.getpreferredencoding()
process = subprocess.Popen(args, stdout=subprocess.PIPE)

for line in process.stdout:
    line = line.decode(encoding)
    print(line)
