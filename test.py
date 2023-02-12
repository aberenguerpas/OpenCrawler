
import Levenshtein
provincias = ['Galicia', 'Comunitat Valenciana', 'Castilla - La Mancha', 'Madrid', 'Andalucía', 'Euskadi', 'Asturias', 'Castilla y León', 'Comunitat Valenciana', 'Ceuta', 'Melilla','La Rioja','Murcia','Cataluña','Aragón', 'Illes Balears', 'Canarias','Extremadura']

max=0
gana = ""
for i in des.split(" "):
    for j in provincias:

        if Levenshtein.ratio(i, j)>max:
            max = Levenshtein.ratio(i, j)
            gana = i

    if max>0.8:
        place = gana
    else:
        place = None
