export FLASK_APP=main.py
.PHONY: run debug doc

run:
	flask --debug run

debug:
	FLASK_DEBUG=1 flask run


doc: doc.raml
	raml2html --input doc.raml --output templates/doc.html --encoding utf8
	# NE FONCTIONNE PAS

rdoc: doc run