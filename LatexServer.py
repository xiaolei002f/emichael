#!/usr/bin/python
# pylint: disable=W0311

import hashlib
import json
import os
import random
import requests
import shutil
import string
import sys
import urllib
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

HOSTNAME = 'myhostname.com'
PORT_NUMBER = 8642

ERROR_IMAGE = 'error.png'

QUICKLATEX_URL = 'http://quicklatex.com/latex3.f'

charset = string.ascii_lowercase + string.digits

def render_QuickLatex(latex_string, dest):
  latex_string = '\\[ %s \\]' % latex_string
  data = {
    'formula': latex_string,
    'fsize': '20px',
    'fcolor': '000000',
    'mode': '0',
    'out': '1',
    'remhost': 'quicklatex.com',
    'preamble': "\\usepackage{amsmath,amsfonts,amsthm,amssymb}",
  }

  response = requests.post(QUICKLATEX_URL,
                           data=urllib.urlencode(data).replace('+', '%20'))
  if response.status_code != 200:
    return

  image_url = response.text.split()[1]
  response = requests.get(image_url, stream=True)
  if response.status_code != 200:
    return

  with open(dest, 'wb') as image_file:
    response.raw.decode_content = True
    shutil.copyfileobj(response.raw, image_file)

  # Add transparent padding
  print os.system('convert %s -bordercolor none -border 5x5 %s' % (dest, dest))

def render_local(latex_string, dest):
  random_string = ''.join(random.choice(charset) for i in range(16))
  tmpfile = '/tmp/%s.tex' % (random_string,)

  latex_file = open(tmpfile, 'w')
  latex_file.write('\\documentclass[12pt,a4paper]{article}\n')
  latex_file.write('\\usepackage{amsmath,amsthm,amssymb,amsfonts}\n')
  latex_file.write('\\usepackage[active,displaymath,tightpage]{preview}\n')
  latex_file.write('\\begin{document}\n')
  latex_file.write('\\[\n %s\n\\]\n' % latex_string)
  latex_file.write('\\end{document}\n')
  latex_file.close()

  # Compile the latex, crop it and convert to png.
  # TODO: use popen to detect errors
  print os.system('pdflatex -output-directory /tmp -halt-on-error ' + tmpfile)
  print os.system('pdfcrop --margins 2 /tmp/%s.pdf' % (random_string,))
  # TODO: output to tmp file, then move to images dir
  print os.system('convert -density 150 /tmp/%s-crop.pdf -quality 90 %s' % (random_string, dest))

  # Cleanup temporary files.
  print os.system('rm -f /tmp/%s*' % random_string)

class LatexHandler(BaseHTTPRequestHandler):
  def do_POST(self):
    # Extract and print the contents of the POST
    length = int(self.headers['Content-Length'])
    post_data = urlparse.parse_qs(self.rfile.read(length).decode('utf-8'))

    latex_string = ' '.join(post_data['text'])

    response = {}
    response['text'] = ""
    response['response_type'] = "in_channel"
    response['attachments'] = [{
      'title': "LaTeX Image (powered by <http://quicklatex.com/|QuickLaTeX>)",
      'fallback': "Could not render equation",
      'image_url':  "http://%s:%s/%s" % (
        HOSTNAME, PORT_NUMBER, urllib.quote(latex_string)),
    }]

    self.send_response(200)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(response))

  # Handler for the GET requests
  def do_GET(self):
    # Create directory images/ in current directory if it does not exist.
    os.system('mkdir -p images/')

    # Extract the latex equation from the URL.
    equation = urllib.unquote(self.path[1:])
    latex_hash = hashlib.sha256(equation)
    image_file = 'images/%s.png' % (latex_hash.hexdigest(),)

    # If the image for this equation exists, return it.
    if os.path.isfile(image_file):
      self.send_image(image_file)
      return

    render_QuickLatex(equation, image_file)

    # If successful, png exists. Send it as http response.
    if not os.path.isfile(image_file):
      os.system('ln -s ../%s %s' % (ERROR_IMAGE, image_file))

    self.send_image(image_file)

  # Sends a png image reply.
  def send_image(self, path):
    with open(path, 'rb') as image_file:
      self.send_response(200)
      self.send_header('Content-type', 'image/png')
      self.end_headers()
      self.wfile.write(image_file.read())

# end LatexHandler


if __name__ == '__main__':
  done = False
  while not done:
    try:
      # Create a web server using latex handler to manage requests.
      server = HTTPServer(('', PORT_NUMBER), LatexHandler)
      print >> sys.stderr, 'Started server on port:', PORT_NUMBER

      # Wait forever for incoming http requests.
      server.serve_forever()

    except KeyboardInterrupt:
      print >> sys.stderr, '^C received, shutting down server.'
      server.socket.close()
      done = True

    except:
      e = sys.exc_info()[0]
      print e
