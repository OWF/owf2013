.PHONY: all

SRC=website

test:
	nosetests tests

run:
	./main.py serve

all:
	./main.py build

clean:
	rm -rf build 
	rm -rf ./static/.webassets-cache
	rm -rf *.egg *.egg-info
	find . -name "*.pyc" | xargs rm -f
	find . -name packed.js | xargs rm -f
	find . -name packed.css | xargs rm -f

push:
	rsync -e ssh -avz --exclude .git --exclude .tox \
		./ dedi:owf2013/

update-pot:
	# _n => ngettext, _l => lazy_gettext
	pybabel extract -F etc/babel.cfg -k "_n:1,2" -k "_l"\
    -o $(SRC)/translations/messages.pot "${SRC}"
	pybabel update -i $(SRC)/translations/messages.pot \
    -d $(SRC)/translations
	pybabel compile -d $(SRC)/translations

