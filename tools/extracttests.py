﻿#!/usr/bin/python

import sys
import re

class Extract:
    nodes = []

    def parseFile(self,filename):
        name = '[0-9a-zA-Z_]+'
        str =  '\\"(.+)\\"'

        testclass = None
        functionName = None

        fin = open(filename, 'r')
        for line in fin:
            # testclass starts
            res = re.match('class ('+name+')', line)
            if res != None:
                testclass = res.group(1)

            # end of testclass 
            if re.match('};', line) != None:
                testclass = None

            # function start
            res = re.match('\\s+void ('+name+')\\(\\)', line)
            if res != None:
                functionName = res.group(1)

            elif re.match('\\s+}', line) != None:
                functionName = None

            if functionName == None:
                continue

            # check
            res = re.match('\s+check\('+str, line)
            if res != None:
                code = res.group(1)

            # code..
            res = re.match('\\s+'+str, line)
            if res != None:
                code = code + res.group(1)

            # assert
            res = re.match('\\s+ASSERT_EQUALS\\(\\"(.*)\\"', line)
            if res != None and len(code) > 10:
                node = { 'testclass':testclass, 'functionName':functionName, 'code':code, 'expected':res.group(1) }
                self.nodes.append(node)
                code = ''

def strtoxml(s):
    return s.replace('&','&amp;').replace('"', '&quot;').replace('<','&lt;').replace('>','&gt;')

if len(sys.argv) == 1 or '--help' in sys.argv:
    print 'Extract test cases from test file'
    print 'Syntax: extracttests.py [--html=folder] [--xml] path/testfile.cpp'

# parse command line
xml = False
filename = None
htmldir = None
i = 1
while i < len(sys.argv):
    if sys.argv[i] == '--xml':
        xml = True
    elif sys.argv[i].startswith('--html='):
        arg = sys.argv[i]
        htmldir = arg[7:]
    else:
        filename = sys.argv[i]
    i = i + 1

# extract test cases
if filename != None:
    # parse test file
    e = Extract()
    e.parseFile(filename)

    # generate output
    if xml:
        print '<?xml version="1.0"?>'
        print '<tree>'
        count = 0
        for node in e.nodes:
            s  = '  <node'
            s += ' function="' + node['functionName'] + '"'
            s += ' code="' + strtoxml(node['code']) + '"'
            s += ' expected="' + strtoxml(node['expected']) + '"'
            s += '/>'
            print s
        print '</tree>'
    elif htmldir != None:
        if not htmldir.endswith('/'):
            htmldir += '/'
        findex = open(htmldir + 'index.htm', 'w')
        findex.write('<html>\n')
        findex.write('<head>\n')
        findex.write('  <style type="text/css">\n')
        findex.write('  table { font-size: 0.8em }\n')
        findex.write('  th { background-color: #A3C159; text-transform: uppercase }\n')
        findex.write('  td { background-color: #F0FFE0; vertical-align: text-top }\n')
        findex.write('  A:link { text-decoration: none }\n')
        findex.write('  A:visited { text-decoration: none }\n')
        findex.write('  A:active { text-decoration: none }\n')
        findex.write('  A:hover { text-decoration: underline; color: blue }\n')
        findex.write('  </style>\n')
        findex.write('</head>\n')
        findex.write('<body>\n')
        findex.write('<h1>' + filename + '</h1>\n')

        functionNames = []
        for node in e.nodes:
            functionname = node['functionName']
            while functionname[-1].isdigit():
                functionname = functionname[:-1]
            if functionname[-1] == '_':
                functionname = functionname[:-1]
            if not functionname in functionNames:
                functionNames.append(functionname)
        functionNames.sort()

        findex.write('<table border="0" cellspacing="0">\n')
        findex.write('  <tr><th>Name</th><th>Number</th></tr>\n')
        for functionname in functionNames:
            findex.write('  <tr><td><a href="'+functionname+'.htm">'+functionname+'</a></td>')
            num = 0
            for node in e.nodes:
                name = node['functionName']
                while name[-1].isdigit():
                    name = name[:-1]
                if name[-1] == '_':
                    name = name[:-1]
                if name == functionname:
                    num = num + 1
            findex.write('<td><div align="right">' + str(num) + '</div></td></tr>\n')

        findex.write('</table>\n')

        findex.write('</body></html>')
        findex.close()

        # create files for each functionName
        for functionName in functionNames:
            fout = open(htmldir + functionName + '.htm', 'w')
            fout.write('<html>\n')
            fout.write('<head>\n')
            fout.write('  <style type="text/css">\n')
            fout.write('  body { font-size: 0.8em }\n')
            fout.write('  th { background-color: #A3C159; text-transform: uppercase }\n')
            fout.write('  td { background-color: white; vertical-align: text-top }\n')
            fout.write('  pre { background-color: #EEEEEE }\n')
            fout.write('  </style>\n')
            fout.write('</head>\n')
            fout.write('<body>\n')
            fout.write('<h1>' + node['testclass'] + '::' + functionName + '</h1>')
            fout.write('<table border="0" cellspacing="0">\n')
            fout.write('  <tr><th>Nr</th><th>Code</th><th>Expected</th></tr>\n')
            num = 0
            for node in e.nodes:
                name = node['functionName']
                while name[-1].isdigit():
                    name = name[:-1]
                if name[-1] == '_':
                    name = name[:-1]
                if name == functionName:
                    num = num + 1
                    fout.write('  <tr><td>' + str(num) + '</td>')
                    fout.write('<td><pre>' + strtoxml(node['code']).replace('\\n', '\n') + '</pre></td>')
                    fout.write('<td>' + strtoxml(node['expected']).replace('\\n', '<br>') + '</td>')
                    fout.write('</tr>\n')
            fout.write('</table></body></html>\n')
            fout.close()
    else:
        for node in e.nodes:
            print node['functionName']

