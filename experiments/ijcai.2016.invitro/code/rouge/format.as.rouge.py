#!/usr/bin/python3
import sys
import re
import os

re_apostrophe = re.compile(u'’')
re_a=re.compile(u'[áâàäãą]')
re_e=re.compile(u'[éèêëěę]')
re_i=re.compile(u'[íïîìı]')
re_o=re.compile(u'[óòôöøōő]')
re_u=re.compile(u'[úùüû]')
re_n=re.compile(u'[ñ]')

html_head = "<html>\n<head>\n"
html_tail = "</body>\n</html>\n"

if len(sys.argv)>1:
    file_name=sys.argv[1]
    with open(file_name, encoding='utf-8') as f:        
        html_title = "<title>" + os.path.basename(file_name) + '</title>\n</head>\n<body bgcolor="white">\n'
        html_head += html_title
        print (html_head, end="")
        line_number = 1
        line_head_format = '<a name="{0:d}">[{0:d}]</a> <a href="#{0:d}" id={0:d}> '
        line_tail_format = "</a>"
        for line in f:
            line = re_a.subn('a',line)[0]
            line = re_e.subn('e',line)[0]
            line = re_i.subn('i',line)[0]
            line = re_o.subn('o',line)[0]
            line = re_u.subn('u',line)[0]
            line = re_n.subn('n',line)[0]
            line = re_apostrophe.subn("'",line)[0]
            line_strip = line.strip()
            if (line_strip):
                printing_line = line_head_format.format(line_number) + line_strip + line_tail_format
                print(printing_line)
                line_number += 1
        print (html_tail, end="")
    
            
