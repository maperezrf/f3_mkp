import io
import pandas               as pd
from   python.cl_cleaning   import CleaningText as ct 
import python.constants     as const

# Variables globales  
tienda, cd, sac, nan = const.tienda, const.cd, const.sac, const.nan

# Global functions 
def delete_initial_rows(text_file):
    file = open(text_file, 'r', encoding='ISO-8859-1')
    flines = file.readlines()[10:]
    file.close()
    return flines

class F3Cleaning():

    def __init__(self, file_name) -> None:
        self.f3_name = file_name

    def clean_f3(self):
        file_path = open('python/config/path.txt')
        path = file_path.readline()
        file_path.close()

        f3_lines = delete_initial_rows(f'{path}/input_planillas/{self.f3_name}.txt')
        f3 = pd.read_csv(io.StringIO("\n".join(f3_lines)), sep=';', dtype='object', on_bad_lines='skip' )
        a = f3.shape[0]

        f3 = ct.norm_header(f3) # Normalizar encabezado 
        # Obtener filas vacias 
        vacias = f3[f3['fecha_reserva'].isna()] 
        f3 = f3[f3['fecha_reserva'].notna()] 
        
        desplazadas = f3[f3.isna().sum(axis=1) >= f3.shape[1]-2]
        indice_des = desplazadas.index
        # Actualiza los valores de F11 desplazados
        for i in indice_des:
            f3.loc[i-1,'nc_proveedor':'folio_f11'] = f3.loc[i,'nro_devolucion':'fecha_reserva'].values
       
        print(f'   {vacias.shape[0]} registros de F11s vacios')
        print(f'   {desplazadas.shape[0]} registros de F11s desplazados')
        res1 = f3[~f3.index.isin(indice_des)]
        
        #print(list(indice_des.isin(f3.index)))
        f3 = f3[f3.isna().sum(axis=1) < f3.shape[1]-2]
        #print(res1[~res1.index.isin(res.index)])
        #print(res.shape)

        # -------------------------------------------------------
        # Revisar info
        # -------------------------------------------------------
        text_cols = ['nro_devolucion', 'tipo_producto', 'descripcion', 'marca', 'subclase',
        'descripcion1', 'clase', 'descripcion2', 'sublinea', 'descripcion3', 'linea', 
        'descripcion4','proveedor', 'descripcion5', 'descripcion6', 'tipo_documento_para_dev',
        'usuario_que_confirma', 'nc_proveedor']

        fnum_cols = ['nro_guia', 'upc', 'sku', 'rut_proveedor', 'local', 'estado', 'folio_f11', 'folio_f12' ]

        num_cols = [ 'cantidad', 'cant*costo', 'cant*costoprmd', 'diferencia', 'cant*precio']
        
        date_cols = [ 'fecha_reserva', 'fecha_envio', 'fecha_anulacion','fecha_confirmacion']

        f3.loc[:, text_cols] = f3.loc[:, text_cols].apply(ct.clean_str)
        f3.loc[:, fnum_cols] = f3.loc[:, fnum_cols].apply(ct.clean_fnum)
        f3.loc[:, num_cols] = f3.loc[:, num_cols].apply(ct.clean_num)

        # Conversion de datos                  
        f3['cant*costoprmd'] = pd.to_numeric(f3['cant*costoprmd']) # Convierte en número la columna cant*costoprmd
        f3["fecha_reserva"] = f3["fecha_reserva"].replace(["ene", "abr", "ago", "dic"], ["jan", "apr", "aug", "dec"], regex=True)  # cambio idioma mes
        f3["fecha_reserva"] = pd.to_datetime(f3["fecha_reserva"], format='%d-%b-%Y')  # cambio de tipo de dato          
        
        # Agrega columna local_agg y filtra por producto market place 
        f3 = f3.loc[f3.tipo_producto == 'market place'].reset_index(drop=True)
        f3.loc[f3.local.isin(tienda), 'local_agg'] = 'TIENDA'
        f3.loc[f3.local.isin(cd), 'local_agg'] = 'CD'
        f3.loc[f3.local.isin(sac), 'local_agg'] = 'SAC'
        f3.loc[f3.local.isin(nan), 'local_agg'] = 'NAN'
        f3.drop('tipo_producto', axis=1, inplace=True)
        f3=f3.rename(columns={'descripcion5':'local_descrip', 'descripcion6':'estado_descrip'})
        
        # Arregla los nombres de las fechas de anulación y confirmación 
        f3 = f3.rename(columns={'fecha_anulacion':'fa', 'fecha_confirmacion':'fc'})
        f3 = f3.rename(columns={'fa':'fecha_confirmacion', 'fc':'fecha_anulacion'})
        return f3 
