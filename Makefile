export FLASK_APP=app.py

run:
	flask run

debug:
	FLASK_DEBUG=1 flask run


doc: doc.raml
	raml2html --input doc.raml --output templates/doc2.html --encoding utf8
	# NE FONCTIONNE PAS