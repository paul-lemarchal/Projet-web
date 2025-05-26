from serveur import get_template, render, OK, Redirect, pageDynamique, lancerServeur
import csv

# Les messages de la conversation
avis = []
contact=[]
reservations=[]
def start(url,vars):
    return Redirect("/index.html")

# La page dynamique qui affiche une conversation
def page_avis(url, vars):
	""" Retourner la page de la conversation """
	# charger le patron
	template = get_template('avis.html')
	# définir les variables
	vars['les_avis'] = avis
	# appliquer le patron
	html = render(template, vars)
	# retourner la page au navigateur
	return OK(html)

# La page dynamique qui ajoute un message
def nouvel_avis(url, vars):
    avis_nouveau = vars['new_avis']
	# l'insérer au début de la conversation
    avis.append(avis_nouveau)
    
    # ouverture en écriture (w, première lettre de write) d'un fichier
    with open('avis.csv', 'w', newline='') as fichier:
        print("fichier ouvert")
        
        # on déclare un objet writer 
        ecrivain = csv.writer(fichier)
        # quelques lignes:
        for element in avis:
            ecrivain.writerow([element])
        fichier.close()
    return Redirect('/avis.html')

def nouveau_contact(url,vars):
    contact_nouveau = vars['new_contact']
    contact.append(contact_nouveau)
    with open('contact.csv', 'w', newline='') as fichier:
        print("fichier ouvert")
        
        ecrivain = csv.writer(fichier)
        for message_contact in contact:
            ecrivain.writerow([message_contact])
        fichier.close()
    return Redirect('/contact.html')

def nouvelle_reservation(url,vars):
    reservation_nouvelle = vars['new_reservation']
    reservations.append(reservation_nouvelle)
    with open('reservations.csv', 'w', newline='') as fichier:
        print("fichier ouvert")
        ecrivain = csv.writer(fichier)
        for reservation in reservations:
            ecrivain.writerow([reservation])
        fichier.close()
    return Redirect('/reserve.html')

pageDynamique('/', start)
pageDynamique('/avis.html', page_avis)
# De même il appelera la fonction `nouveau_message`
# lorsqu'il recevra une requête pour la page `/message`.
pageDynamique('/avis_ajout', nouvel_avis)
pageDynamique('/contact_ajout', nouveau_contact)
pageDynamique('/reservation_ajout',nouvelle_reservation)

# Lancer le serveur
lancerServeur()