pyrcc = pyrcc5
pyuic = pyuic5
lrelease = "lrelease"

rccargs = -compress 12 -threshold 1
uicargs =

all: i18n res.py untitled.py aboutdiag.py

.PHONY : clean
clean:
	rm -rf res.py
	rm -rf *.qm
	rm -rf untitled.py
	rm -rf aboutdiag.py

.PHONY : i18n
i18n:
	$(python) compilei18n.py $(lrelease) "./i18n/"
	mv i18n/untitled.*.qm ./

res.py:
	$(pyrcc) $(rccargs) res.qrc

untitled.py aboutdiag.py:
	$(pyuic) $(uicargs) untitled.ui
	$(pyuic) $(uicargs) aboutdiag.ui
