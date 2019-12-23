import subprocess

BLUE =  '\033[1;38;2;32;64;227m'
RED =   '\033[1;38;2;227;32;32m'
GREEN = '\033[0;38;2;0;192;0m'
YELLOW ='\033[0;38;2;192;192;0m'
NC =    '\033[0m'

# for executing shell commands
def cmdLine(cmd):
    process = subprocess.Popen(args = cmd, stdout = subprocess.PIPE, universal_newlines = True, shell = True)
    return process.communicate()[0]

def cmdLineWaitUntilExecution(cmd):
    process = subprocess.call(args = cmd, stdout = subprocess.PIPE, universal_newlines = True, shell = True)
    #return process.communicate()[0]