export FLASK_APP=app.py

run:
	flask --debug run

doc:
	raml2html --input doc.raml --output templates/doc2.html --encoding utf8
	# NE FONCTIONNE PAS