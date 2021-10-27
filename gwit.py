import xml.etree.ElementTree as ET
import sys
import re
import os
from sys import exit
from fnmatch import fnmatch
from shutil import copyfile

def mkDirP(dirs):
    if not os.path.exists(dirs):
        try:
            os.makedirs(dirs)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

# witness tmp dir
# TODO: actual tmp dir?
wtTmp="wtTmp"
mkDirP(wtTmp)


# parse arguments
if len(sys.argv) <= 2:
    if sys.argv[1] == '--version' :
        print('0.1')
    exit(0)
else:
    witness_file = sys.argv[1]
    classpath = {}
    for cp in sys.argv[2:]:
        for path, dirs, files in os.walk(cp):
            for name in files:
                if fnmatch(name, '*.java'):
                    package = path.replace(cp,'')[1:]
                    filename = os.path.join(path, name)
                    classname = name
                    if len(package) != 0:
                        classname = package + "/" + classname
                    classpath[classname] = filename

#print(classpath)


# load witness
with open(sys.argv[1]) as f:
    xmlstring = f.read()

xmlstring = re.sub(r'\sxmlns="[^"]+"', '', xmlstring, count=1)
witness = ET.fromstring(xmlstring)

# TODO: check on type of witness



# find edge assumptions
assumptions = {}
for e in witness.findall(".//data[@key='assumption']/.."):
    assume = e.find("data[@key='assumption']").text
    assume = assume.replace(';', '').replace('=', '==')
    file = e.find("data[@key='originfile']").text
    line = e.find("data[@key='startline']").text
    scope = e.find("data[@key='assumption.scope']").text
    # print(scope + " : " + assume)
    # FIXME: this breaks for static values that are 
    # initialized by Verifier.nondet(...)
    # if such instances exist, we may have to change 
    # Witness class implementation.
    if "clinit" not in scope and "java" != scope:
        if file not in assumptions:
            assumptions[file] = {}
        if line not in assumptions[file]:
            assumptions[file][line] = [assume]
        else:
            assumptions[file][line].append(assume)

#print(assumptions)

uid = 0
for classname in classpath:
    filename = classpath[classname]
    mkDirP( os.path.dirname(wtTmp + "/" + classname))
    oname = wtTmp + "/" + classname
    if classname not in assumptions:
        # copy file
        copyfile(filename, oname)
    else:
        # print("Assumptions on: " + classname)
        with open(classpath[classname],'r') as fin:
            with open(oname, 'wt') as fout:
                for pos,line in enumerate(fin,1):
                    # print(str(pos) + " " + line)
                    if line.strip().startswith('class') or line.strip().startswith('public class'):
                        fout.write("import org.sosy_lab.sv_benchmarks.Witness;\n\n")
                    if str(pos) in assumptions[classname]:
                        #print("  Assumptions on line: " + line)
                        varargs = ', '.join(assumptions[classname][str(pos)])
                        assumeCode = " Witness.assume(" + str(uid) + ", " + varargs + ");\n"
                        uid += 1
                        #print(assumeCode)
                        line += assumeCode
                    fout.write(line)
