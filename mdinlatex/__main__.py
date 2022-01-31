#!/usr/bin/env python3
import os, sys, argparse, markdown
from fileinput import FileInput as finput
from bs4 import BeautifulSoup

def arguments(string_set):
	parser = argparse.ArgumentParser(description=f"Insert Markdown code into Latex File Section.")

	parser.add_argument("-s",
						"--source",
						dest="source",
						action="store",
						help="The source markdown file",
						default="main.md")

	parser.add_argument("-o",
						"--output",
						dest="output",
						action="store",
						help="The output latex file",
						default="main.tex")

	parser.add_argument("--START",
						dest="START",
						action="store",
						help="The starting of the section to insert into",
						default="%%START")

	parser.add_argument("--END",
						dest="END",
						action="store",
						help="The ending of the section to insert into",
						default="%%END")

	return parser.parse_args(string_set)

def grab_link_text(line):
    grab_links = lambda tag: (getattr(tag, 'name', None) == 'a' and 'href' in tag.attrs)
    
    for result in BeautifulSoup(line, features="html.parser").find_all(grab_links):
       newString = f"\\href{{ {result['href']} }}{{ {result.text.strip()} }}" 
       line = line.replace(str(result), str(newString))

    return line

def grab_code(line):
    grab_links = lambda tag: (getattr(tag, 'name', None) == 'code')
    
    for result in BeautifulSoup(line, features="html.parser").find_all(grab_links):
        line = f"""
\\begin{{figure}}[H]
    \\centering\\hspace*{{-0.75in}}
    \\begin{{lstlisting}}[language=Python,escapechar=@,caption={{CAPTION HERE}}, captionpos=b,label={{lst:python_label}}]
{result.text.strip()} 
    \\end{lstlisting}
\\end{figure}
"""

    return line

if __name__ == '__main__':
	self_name = os.path.basename(__file__)
	args = arguments(list(filter(lambda x: not str(x).endswith(self_name), sys.argv)))
	no_tags = lambda string,tag: string.replace(f"<{tag}>","").replace(f"</{tag}>","")
	no_cmt = lambda string: string.split("%")[0]

	lines = []
	if os.path.exists(args.source):
		with open(args.source,"r") as reader:
			for line in markdown.markdown(reader.read()).split("\n"):
				try:
					section_name = "se:"+line.split(">")[1].split("<")[0].replace(' ','')
				except:
					section_name = "se:"
				prefix = "section"

				if line.startswith("<h1>"):
					rawd = no_tags(line,"h1")
				elif line.startswith("<h2>"):
					rawd = no_tags(line,"h2")
					section_name = "s" + section_name
					prefix = "sub" + prefix
				elif line.startswith("<h3>"):
					rawd = no_tags(line,"h3")
					section_name = "ss" + section_name
					prefix = "subsub" + prefix
				elif line.startswith("<ul>"):
					rawd = "\\begin{itemize}"
					section_name = None
					prefix = None
				elif line.startswith("</ul>"):
					rawd = "\\end{itemize}"
					section_name = None
					prefix = None
				elif line.startswith("<li>"):
					rawd = "\t\\item " + no_tags(line,"li")
					section_name = None
					prefix = None
				elif "<code>" in line:
					rawd = grab_code(line)
					section_name = None
					prefix = None
				else:
					rawd = no_tags(line,"p")
					prefix = None
					section_name = None

				rawd = grab_link_text(no_cmt(rawd))
				if section_name:
					section_name = no_cmt(section_name)

				if section_name and section_name:
					string = f"\\{prefix}{{ {rawd} }} \\label{{ {section_name} }}".replace("\\\\","\\")
				else:
					string = rawd

				lines += [
					string
				]

	write_into, within = False,False
	with finput(args.output,inplace=True) as foil:
		for line in foil:
			stripped = line.strip()

			if stripped == args.START:
				write_into = True

			if stripped == args.END:
				within = False

			if write_into and stripped != args.START:
				for line in lines:
					print(line)
				write_into = False
				within = True

			if not within:
				print(line, end='')
