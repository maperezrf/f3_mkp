import pandas as pd
from python.f3_mkp import F3MKP
import numpy as np
f3mkp = F3MKP()
pd.set_option('display.max_columns', 500)
file = input("por favor ingrese el nombre del archivo a distribuir: ")
f3_red = pd.read_excel(f"{f3mkp.path}/input_planillas/{file}.xlsx")
list_dist = f3_red.nro_devolucion.unique()
f3mkp.load_consolidado()
f3mkp.consolidado.nro_devolucion = pd.to_numeric(f3mkp.consolidado.nro_devolucion)
list =f3mkp.consolidado.loc[(f3mkp.consolidado.nro_devolucion.isin(list_dist))].nro_devolucion
indice = f3mkp.consolidado.loc[(f3mkp.consolidado.nro_devolucion.isin(list_dist)) &   (f3mkp.consolidado["dup_f3"]!='no') ,'indice_f3']
f3mkp.consolidado.loc[(f3mkp.consolidado.indice_f3.isin(indice)), 'digitador_responsable'] = np.nan
f3mkp.consolidado.loc[(f3mkp.consolidado.indice_f3.isin(indice)), 'tipificacion_1'] = np.nan
if len(list_dist) == f3mkp.consolidado.loc[(f3mkp.consolidado.indice_f3.isin(indice))].shape[0]:
    f3mkp.guardar_consolidado()
else:
    print("----NO SE PUEDE GUARDAR EL CONSOLIDADO---")