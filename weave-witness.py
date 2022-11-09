# SPDX-FileCopyrightText: 2021 Falk Howar falk.howar@tu-dortmund.de
# SPDX-License-Identifier: Apache-2.0

import xml.etree.ElementTree as ET
import sys
import re
import os
import tempfile
from sys import exit
from fnmatch import fnmatch
from shutil import copyfile
# import yaml

def mkDirP(dirs):
    if not os.path.exists(dirs):
        try:
            os.makedirs(dirs)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

# parse arguments
if len(sys.argv) <= 2:
    if len(sys.argv) > 1 and sys.argv[1] == '--version':
        print('0.1')
    else:
        print('usage: python3 weave-witness.py [witness_file] [list of folders]')
    exit(0)
else:
    witness_file = sys.argv[1]
    classpath = {}
    # conf = {}
    # with open(property_file, "r") as stream:
    #    try:
    #        conf = yaml.safe_load(stream)            
    #    except yaml.YAMLError as e:
    #        raise
    #for cp in conf['input_files']:
    for cp in sys.argv[2:]:
        if cp.endswith("/common/"):
            continue
        # cp = os.path.dirname(property_file) + "/" + cp
        for path, dirs, files in os.walk(cp):
            for name in files:
                if fnmatch(name, '*.java'):
                    package = path.replace(cp,'') 
                    filename = os.path.join(path, name)
                    classname = name
                    if len(package) != 0:
                        classname = package + "/" + classname
                    classpath[classname] = filename

# load witness
with open(witness_file) as f:
    xmlstring = f.read()

xmlstring = re.sub(r'\sxmlns="[^"]+"', '', xmlstring, count=1)
witness = ET.fromstring(xmlstring)

# check on type of witness
wtype = witness.find(".//data[@key='witness-type']").text
if wtype != 'violation_witness':
    exit(0)

# find edge assumptions
assumptions = {}
for e in witness.findall(".//data[@key='assumption']/.."):
    assumption_parts = list(e.find("data[@key='assumption']").itertext())
    if len(list(e.find("data[@key='assumption']").iter())) > 1 and list(e.find("data[@key='assumption']").iter())[1].tag == "bad" and len(assumption_parts) == 2:
        assume = assumption_parts[0] + "<bad/>" +assumption_parts[1]
    else:
        assume = assumption_parts[0]
    assume = assume.replace(';', '').replace('=', '==')
    file = e.find("data[@key='originfile']").text
    line = e.find("data[@key='startline']").text
    scope = e.find("data[@key='assumption.scope']").text
    #print(scope + " : " + assume)
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

# print(assumptions)

# weave witness and instance
wtTmp = tempfile.mkdtemp()
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
                        fout.write("import tools.aqua.concolic.Witness;\n\n")
                    if str(pos) in assumptions[classname]:
                        #print("  Assumptions on line: " + line)
                        varargs = ', '.join(assumptions[classname][str(pos)])
                        assumeCode = " Witness.assume(" + str(uid) + ", " + varargs + ");\n"
                        uid += 1
                        #print(assumeCode)
                        line += assumeCode
                    fout.write(line)
print(wtTmp)

