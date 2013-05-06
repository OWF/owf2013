.PHONY: all

SRC=website

run:
	./main.py serve

all:
	./main.py build

clean:
	rm -rf build
	rm -rf ./static/.webassets-cache
	find . -name "*.pyc" | xargs rm -f
	find . -name packed.js | xargs rm -f
	find . -name packed.css | xargs rm -f

push:
	rsync -e ssh -avz ./ dedi:owf2013/

update-pot:
	# _n => ngettext, _l => lazy_gettext
	pybabel extract -F etc/babel.cfg -k "_n:1,2" -k "_l"\
    -o $(SRC)/translations/messages.pot "${SRC}"
	pybabel update -i $(SRC)/translations/messages.pot \
    -d $(SRC)/translations
	pybabel compile -d $(SRC)/translations

