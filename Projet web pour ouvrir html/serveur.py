# -*- coding: utf8 -*-
#
#	Serveur Web permettant de gérer des pages dynamiques
#	Il n'y a pas de modifications à faire dans ce fichier
#

from http.server import SimpleHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import urlparse, parse_qs
from os import curdir, chdir

# Le numéro de port du serveur. Son URL est donc http://localhost:8000/
PORT = 8005

# Se mettre dans le dossier "www". Les chemins des URLs sont donc relatives à ce dossier
# chdir("www")

# Configurer la bibliothèque de gestion des templates
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

# Fonctions exportées pour faciliter l'utilisation des patrons
def get_template(t):
	return env.get_template(t)

def render(t, v):
	return t.render(v)

# Mémoriser les chemins qui correspondent à des pages dynamiques
pagesDynamiques = {}
def pageDynamique(path, f):
	pagesDynamiques[path] = f

# Parse query string and replace 1-element arrays by the value of their element
def parse_query(q):
	query = parse_qs(q, keep_blank_values=1)
	for var in query:
		if len(query[var]) == 1:
			query[var] = query[var][0]
	return query

# Cette classe décrit comment traiter les requêtes reçues par le serveur
class mesRequetes(SimpleHTTPRequestHandler):
	
	def executeDynamicPage(self, path, vars):
		code, headers, content = pagesDynamiques[path](path, vars)
		self.send_response(code)
		for (header,value) in headers:
			self.send_header(header, value)
		self.end_headers()
		if content is not None:
			self.wfile.write(content.encode("utf-8"))

	# Traitement d'une requête GET
	def do_GET(self):
		parsed = urlparse(self.path)
		path = parsed.path
		if len(parsed.query) > 0:
			query = parse_query(parsed.query)
		else:
			query = {}

		# Si le chemin est une page dynamique, exécuter celle-ci pour récupérer son contenu
		if path in pagesDynamiques:
			self.executeDynamicPage(path, query)
			return

		super().do_GET()

	def do_POST(self):
		ctype, pdict = parse_header(self.headers['content-type'])
		if ctype == 'multipart/form-data':
			postvars = parse_multipart(self.rfile, pdict)
		elif ctype == 'application/x-www-form-urlencoded':
			length = int(self.headers['content-length'])
			postvars = parse_query(self.rfile.read(length).decode('utf-8'))
		else:
			postvars = {}

		if self.path in pagesDynamiques:
			self.executeDynamicPage(self.path, postvars)
			return

		self.send_error(404,'File Not Found: %s' % self.path)

# Initialiser le serveur et attendre les requêtes.
# On peut arrêter le serveur en tapant ^C
def lancerServeur():
	try:
		# Créer le serveur HTTP en lui indiquant la classe qui traite les requêtes
		serveur = HTTPServer(('', PORT), mesRequetes)
		print('Serveur prêt sur le port ', PORT)
		
		# Traiter les requêtes
		serveur.serve_forever()

	except KeyboardInterrupt:
		print('Interruption par ^C. Arrêt du serveur.')
		serveur.socket.close()

def OK(content):
	return (200, [], content)

def NotFound(nom):
	return (404, [], "<html><head><meta charset='utf-8'><title>Erreur 404</title><body><h2>Erreur 404</h2><p>"+nom+" : ressource non trouvée</p></body></html>")

def BadRequest(msg):
	return (400, [], "<html><head><meta charset='utf-8'><title>Erreur 400</title><body><h2>Erreur 400</h2><p>Requête incorrecte : "+msg+"</p></body></html>")

def Redirect(url):
	return (301, [('Location', url)], None)

if __name__ == "__main__":
	lancerServeur()
