ui:
	pyuic4 ui_lector.ui > ui_lector.py

resources:
	pyrcc4 -o resources_rc.py resources.qrc

res: resources

translation:
	lrelease-qt4 ts/qt_it_IT.ts
	lrelease-qt4 lector.pro

up_translation:
	pylupdate4 lector.pro

all: ui translation res

clean:
	rm -f ui_lector.py resources_rc.py ts/qt_it_IT.qm ts/lector_*.qm *.pyc
