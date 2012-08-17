"""
Pandoc integration for sublime text markdown.

Allows the user to export their markdown script to a number of different formats.
Currently supported:
 - html
 - pdf
 - docx

Original Author: jclement (https://github.com/jclement/SublimePandoc)
PDF integration: Daniel Mescheder
"""

import sublime, sublime_plugin
import webbrowser
import tempfile
import os
import sys
import subprocess

class PandocRenderCommand(sublime_plugin.TextCommand):

    def is_enabled(self):
        return self.view.score_selector(0, "text.html.markdown") > 0

    def is_visible(self):
        return True 

    def run(self, edit, target="pdf", openAfter=True, saveResult=False, additionalArguments=[]):
        if not target in ["html","docx","pdf"]: raise Exception("Format %s currently unsopported" % target)

        encoding = self.view.encoding()
        if encoding == 'Undefined':
            encoding = 'UTF-8'
        elif encoding == 'Western (Windows 1252)':
            encoding = 'windows-1252'
        contents = self.view.substr(sublime.Region(0, self.view.size()))

        # write buffer to temporary file
        # This is useful because it means we don't need to save the buffer
        tmp_md = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
        tmp_md.write(contents)
        tmp_md.close()

        # output file...
        suffix = "." + target
        if saveResult:
            output_name = os.path.splitext(self.view.file_name())[0]+suffix
            if not self.view.file_name(): 
                raise Exception("Please safe the buffer before trying to export with pandoc.")
        else:
            output = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            output.close()
            output_name = output.name

        args = self.pandoc_args(target)
        self.run_pandoc(tmp_md.name,output_name,args)
        if openAfter: self.open_result(output_name,target)

    def run_pandoc(self, infile, outfile,args):
        cmd  = ['pandoc'] + args
        cmd += [infile, "-o", outfile]
        try:
            subprocess.call(cmd)
        except Exception as e:
            sublime.error_message("Unable to execute Pandoc.  \n\nDetails: {0}".format(e))


    def pandoc_args(self,target):
        """
        Create a list of arguments for the pandoc command
        depending on the target.
        TODO: Actually do something sensible here
        """
        if target == "pdf":
            return []
        if target == "html":
            return ['-t', 'html5']
        if target == "docx":
            return ['-t', 'docx']

    def open_result(self,outfile,target):
        if target == "html":
            webbrowser.open_new_tab(outfile)
        elif sublime.platform() == "windows":
            os.startfile(outfile)
        elif sublime.platform() == "osx":
            subprocess.call(["open", outfile])
        elif sublime.platform() == "linux":
            subprocess.call(["xdg-open", outfile])

