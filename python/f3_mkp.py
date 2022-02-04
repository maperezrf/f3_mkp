import pandas as pd
from datetime import datetime
import numpy as np
from os import listdir, mkdir
from os.path import isfile, join
import python.constants as const
from python.f3_cleaning import F3Cleaning
import plotly.express as px
from python.cl_cleaning import CleaningText as ct 


Fecha = datetime.now().strftime('%d-%m-%Y')

class F3MKP():
    dt_string   = datetime.now().strftime('%y%m%d')
    kpi         = pd.DataFrame()
    consolidado = pd.DataFrame()
    planilla = pd.DataFrame()
    digitadores = const.get_digitadores()

    def __init__(self) -> None:
        f3_name        = input('Ingrese nombre de planilla F3: ')
        self.kpi_name  = input('Ingrese nombre de archivo kpi: ')
        self.f3c       = F3Cleaning(f3_name) # Inicializa la clase de limpieza para la planilla de f3
        with open('python/config/path.txt', "r") as tf:
                self.path = tf.read()
                self.path = self.path.replace("\\","/")
        tf.close()

    def build_planilla(self):
        self.load_srx_files()
        self.kpi["USR"] = self.kpi["USR"].str.strip()
        self.planilla = self.get_f3_user_df()
        duplicados = self.planilla.loc[self.planilla.duplicated(['nro_devolucion', 'upc', 'cantidad'])]
        duplicados.to_excel(f'{self.path}/output_planillas/errores/{self.dt_string}_f3_duplicados.xlsx')
        self.planilla.drop_duplicates(['nro_devolucion', 'upc', 'cantidad'], inplace=True)
        self.set_estado_agg()
        self.set_local_agg()
        self.search_f11_f12()
        self.ident_dupl()

    def search_f11_f12(self):
        self.planilla['folio_f11'] = self.planilla.folio_f11.str.extract(r'([1][1]\d{7,})')
        self.planilla['folio_f12'] = self.planilla.folio_f12.str.extract(r'([1][2]\d{7,})')
        self.planilla['ncp_f11'] = self.planilla.nc_proveedor.str.extract(r'^([1][1]\d{7,})')
        self.planilla['ncp_f12'] = self.planilla.nc_proveedor.str.extract(r'^([1][2]\d{7,})')
        self.planilla['rtv_f11'] = self.planilla.rtv_notes.str.extract(r'([1][1]\d{7,})')
        self.planilla['rtv_f12'] = self.planilla.rtv_notes.str.extract(r'([1][2]\d{7,})')
        self.planilla.folio_f11.fillna(self.planilla.ncp_f11, inplace=True)
        self.planilla.folio_f12.fillna(self.planilla.ncp_f12, inplace=True)
        self.planilla.folio_f11.fillna(self.planilla.rtv_f11, inplace=True)
        self.planilla.folio_f12.fillna(self.planilla.rtv_f12, inplace=True)
        self.planilla.drop(['ncp_f11', 'ncp_f12','rtv_notes', 'rtv_f11','rtv_f12'], axis=1, inplace=True)
    
    def ident_dupl(self):
        planilla_auxf11  = self.planilla.groupby(["folio_f11","upc","cantidad"])["nro_devolucion"].nunique().reset_index()
        planilla_auxf12 = self.planilla.groupby(["folio_f12","upc","cantidad"])["nro_devolucion"].nunique().reset_index()
        indice_f11 = planilla_auxf11.loc[planilla_auxf11.nro_devolucion > 1].folio_f11
        indice_f12 = planilla_auxf12.loc[planilla_auxf12.nro_devolucion > 1].folio_f12
        self.planilla.loc[self.planilla.folio_f11.isin(indice_f11), "duplicado"] = "duplicado"
        self.planilla.loc[self.planilla.folio_f12.isin(indice_f12), "duplicado"] = "duplicado"
        grup = self.planilla.groupby(['nro_devolucion','folio_f12'])["upc"].nunique().reset_index()  # TODO  pasar a metodo y .loc[duplicated('nro_devolucion), 'dup_f3'] ='y'.loc[~duplicated('nro_devolucion), 'dup_f3'] ='n'
        dup = grup.loc[grup.upc > 1].nro_devolucion
        self.planilla.loc[self.planilla.nro_devolucion.isin(dup),'dup_f3'] = "no"
        self.planilla.reset_index()
        duplicados = self.planilla.loc[self.planilla.nro_devolucion.isin(dup)].iloc[:,0:1].reset_index()
        list_si = duplicados.drop_duplicates("nro_devolucion").iloc[:,0]
        self.planilla.loc[self.planilla.index.isin(list_si),"dup_f3"] = "si"

    def build_consolidado(self):
        self.load_consolidado()
        self.build_planilla()
        self.planilla["aux_f12"] = self.consolidado.folio_f12
        self.planilla.folio_f12.fillna(self.planilla.aux_f12,inplace=True)
        self.planilla.drop(['nro_guia', 'subclase', 'descripcion1', 'clase', 'descripcion2', 'sublinea', 'descripcion3','linea', 'descripcion4', 'estado', 'cant*costo', 'diferencia', 'cant*precio', 'usuario_que_confirma',"aux_f12"], axis=1, inplace=True)
        self.consolidado = self.planilla.merge(self.consolidado[const.cols_a_incoporar_consolidado_a_planilla], how="left" , on=["nro_devolucion","upc", "cantidad"]) 
        self.consolidado = self.consolidado.reindex(columns=const.cols_consolidado)
        self.consolidado.reset_index(inplace=True)
        self.consolidado.rename(columns = {"index": "indice_f3"}, inplace=True)
        #self.rdate_filter()

    def load_srx_files(self) -> None:
        # Files loading
        self.kpi = pd.read_excel(f"{self.path}/input_planillas/{self.kpi_name}.xlsx", usecols=["F3", "PRD_UPC","RTV_NOTES", "USR"], dtype=str)  # Load kpi file
        self.planilla = self.f3c.clean_f3()   # Load f3 db

    def load_consolidado(self) -> None:
        self.consolidado = pd.read_excel(f'{self.path}/consolidado/consolidado_f3_marketplace.xlsx', sheet_name='DB',
                          dtype=str,keep_default_na=False,na_values=[""]).rename(columns={'fecha_revision':'dg_fecha_revision','soporte_es_una_guia_de_transportadora':'dg_soporte_guia_transp',  
                      'ndeg_guia_/_carta_cambio': 'dg_n_guia/_carta_cambio',
                      'transportadora':'dg_transportadora',
                      'estado_entregado_de_guia_en_la_plataforma_de_la_transportadora':'dg_entregado_guia_plataf_transp',
                      'nombre_del_seller_en_el_destinatario':'dg_seller_en_destinatario',
                      'direccion_del_seller_corresponde':'dg_direccion_seller',
                      'dg_f12_corresponde':'dg_f12_f11_corresponde', 
                      'f3_corresponde':'dg_f3_corresponde'
                                            },)

    def get_planilla(self):
        return self.planilla
    
    def get_consolidado(self):
        return self.consolidado

    def get_f3_user_df(self):
        # Planilla and kpi merge
        self.kpi = self.kpi.rename(columns={"F3":"nro_devolucion","RTV_NOTES":"rtv_notes","PRD_UPC":"upc", 'USR':'usuario_creacion'})
        pmk      = self.planilla.merge(self.kpi, how="left", on=["nro_devolucion", "upc"])
        return pmk 

    def set_estado_agg(self):
        self.planilla.loc[self.planilla['estado_descrip'].isin(["reservado", "enviado"]), "estado_agg"] = "abierto"
        self.planilla.loc[self.planilla['estado_descrip'].isin(["confirmado", "anulado"]), "estado_agg"] = "cerrado"
    
    def set_local_agg(self):
        self.planilla.loc[self.planilla["usuario_creacion"] == "JROCHA", "local_agg"] = "SAC"

    def rdate_filter(self, date = '2021-01-01'):
        self.planilla = self.planilla.loc[self.planilla.fecha_reserva >= date].reset_index(drop=True)

    def div_planilla(self, digitadores = list(digitadores.values())):
        df_a_distribuir_f = self.consolidado.loc[(self.consolidado.estado_agg == "abierto" ) & (self.consolidado.local_agg != "NAN")  & (self.consolidado.folio_f12.notna()) & (self.consolidado.proveedor != "linio colombia s.a.s.") & (self.consolidado.dup_f3 != "no") & (self.consolidado.duplicado.isna()) & (self.consolidado['digitador_responsable'].isna())]
        if df_a_distribuir_f.shape[0] > 0:
            cantidad_a_distribuir= df_a_distribuir_f.groupby("local_agg")["nro_devolucion"].count()
            print(cantidad_a_distribuir)
            df_a_distribuir_f = df_a_distribuir_f.sort_values(["local_agg","local"])#ordena el df x local_agg y 
            df_a_distribuir_f = df_a_distribuir_f[const.cols_para_digitador]
            div = np.array_split(df_a_distribuir_f, len(digitadores))
            lista_df_x_digitador = []
            for i, df in enumerate(div): 
                digitador = digitadores[i]
                df['digitador_responsable'] = digitador
                self.consolidado.loc[df.index, "digitador_responsable"] = digitador
                lista_df_x_digitador.append([ digitador , df])
            self.save_dfs(lista_df_x_digitador)
            self.save_repo()
            
        else: 
            print('-- Out: No hay registros para distribuir')

    def save_repo(self):
        path = self.path + "/consolidado"
        reporte_local_agg = self.consolidado.groupby(["digitador_responsable","local_agg"])["cantidad"].count().reset_index()
        reporte_local_agg["fecha_distribucion"] = datetime.now().strftime(('%Y-%m-%d'))
        reporte_local_descrip = self.consolidado.groupby(["digitador_responsable","local_descrip"])["cantidad"].count().reset_index()
        reporte_local_descrip["fecha_distribucion"] = datetime.now().strftime(('%Y-%m-%d'))
        reporte_local_agg.to_excel(f'{path}/Reporte_distribucion_agg.xlsx',index=False)
        reporte_local_descrip.to_excel(f'{path}/Reporte_distribucion_local.xlsx',index=False)
        print(f"-- El reporte  de distribución se guardó con éxito, ubicación: {path} ")

    def save_linio(self, path):   
        linio = self.consolidado.loc[(self.consolidado.estado_agg == "abierto" ) & (self.consolidado.proveedor == "linio colombia s.a.s.")] #TODO revisar posicion
        linio.to_excel(f"{path}/{self.dt_string}_linio.xlsx",sheet_name = 'DB', index=False)
        print(f" --Se ha guardado el informe de F3 proveedor linio ubicacion: {path}")
    
    def save_duplicados(self, path):
        duplicados = self.consolidado.loc[(self.consolidado.estado_agg == "abierto" ) & (self.consolidado.local_agg != "NAN")  & (self.consolidado.folio_f12.notna()) & (self.consolidado.duplicado.notna())]
        duplicados.to_excel(f"{path}/{self.dt_string}_duplicados.xlsx",sheet_name = 'DB', index=False)
        print(f" --Se ha guardado el informe de F3 duplicados ubicacion: {path}")

    def save_f3_sin_f12(self, path):
        f3_sin_f12 = self.consolidado.loc[self.consolidado.folio_f12.isna() & (self.consolidado.estado_agg == "abierto")]
        f3_sin_f12.to_excel(f"{path}/{self.dt_string}_f3_sin_f12.xlsx",sheet_name = 'DB', index=False)
        print(f" --Se ha guardado el informe de F3 sin F12 ubicacion: {path}")

    def save_dfs(self, lista_dist):
        path_admin = self.path +f"/distribución/gestión_administrador/{self.dt_string}"
        path_digitador = self.path +f"/distribución/gestión_digitador/{self.dt_string}"
        mkdir(path_admin)
        mkdir(path_digitador)
        self.guardar_consolidado()
        for digitador, df in lista_dist:
            aux_name = f'{self.dt_string}_dist_{digitador}'
            df.to_excel(f'{path_digitador}/{aux_name}.xlsx',sheet_name = aux_name, index=False)
            print(f'Archivo {self.dt_string}_dist_{digitador} guardado con éxito') 
        self.save_linio(path_admin)
        self.save_f3_sin_f12(path_admin)
        self.save_duplicados(path_admin)

    def unir_planillas_d(self,folder):
        path = self.path +f"/distribución/gestión_digitador/{folder}"
        files_names = [f for f in listdir(path) if isfile(join(path, f))]
        files_store = []
        for i in files_names: 
            files_store.append(pd.read_excel(f'{path}/{i}',dtype=object,keep_default_na=False,na_values=[""]))
        nc_df = pd.concat(files_store)
        # nc_df["entregado_a_adm"] =+ 1 #TODO este comando poner mas adelante
        return nc_df
    
    def compare_dfs(self,dist_digitadores):
        self.load_consolidado()
        dist_consolidado = self.consolidado.loc[(self.consolidado.digitador_responsable.notna()) & (self.consolidado.tipificacion_1.isna()), const.cols_a_validar]
        if dist_consolidado.shape[0] == dist_digitadores.shape[0]:
            dist_consolidado["indice_f3"] = pd.to_numeric(dist_consolidado.indice_f3)
            dist_digitadores["indice_f3"] = pd.to_numeric(dist_digitadores.indice_f3)
            dist_digitadores = dist_digitadores.sort_values("indice_f3",axis=0)
            dist_digitadores = dist_digitadores[const.cols_a_validar].sort_values(["indice_f3"])
            dist_digitadores = dist_digitadores.set_index("indice_f3")
            dist_consolidado = dist_consolidado.set_index("indice_f3")
            comparacion = dist_consolidado.compare(dist_digitadores, align_axis=1)    
            si_cambio = comparacion.index
            return si_cambio
        else:
            print("Error: Número de registros distribuidos en consolidado diferente a planilla")
            return []

    def disponibilizar_no_gest(self, si_cambio):
        self.consolidado["indice_f3"] = pd.to_numeric(self.consolidado.indice_f3) #TODO revisar posicion
        self.consolidado.loc[(~self.consolidado.indice_f3.isin(si_cambio)) & (self.consolidado.tipificacion_1.isna()), ["digitador_responsable", "entregado_a_adm" ]] = np.nan
        
    def guardar_consolidado(self):
        path = self.path + "/consolidado" 
        self.consolidado.to_excel(f'{path}/consolidado_f3_marketplace.xlsx',sheet_name = 'DB', index=False) 
        print(f"--El consolidado se guardó ubicación: {path}")
    
    def agregar_gestionados(self, si_cambio, dist_digitadores):
        dist_digitadores = dist_digitadores.set_index("indice_f3")
        lista = const.cols_a_validar + const.cols_a_agregar + ["dg_fecha_revision","dg_n_guia/_carta_cambio","dg_transportadora"]
        lista.remove('indice_f3') 
        self.consolidado.loc[self.consolidado.indice_f3.isin(si_cambio), lista ] = dist_digitadores.loc[si_cambio, lista].values
        
    def validate_df(self, si_cambio,dist_digitadores): 
        dist_digitadores = dist_digitadores.reindex(columns = dist_digitadores.columns.tolist() + (const.cols_a_agregar))
        dist_digitadores = dist_digitadores.loc[dist_digitadores.indice_f3.isin(si_cambio)]
        sop_g = (dist_digitadores.dg_soporte_guia_transp)
        est_en = (dist_digitadores.dg_entregado_guia_plataf_transp)
        nomb_sel = (dist_digitadores.dg_seller_en_destinatario)
        dir_sel = (dist_digitadores.dg_direccion_seller)
        f12_f3 = ((dist_digitadores.dg_f12_f11_corresponde == "si") | (dist_digitadores.dg_f3_corresponde == "si"))       
        list_dir_no_coinc = dist_digitadores.loc[(sop_g == "si") & (est_en == "si") & (nomb_sel == "si") & (dir_sel == "no") & (f12_f3)].nro_devolucion
        list_dir_no_coinc2 = dist_digitadores.loc[(sop_g == "no") & (est_en == "na") & (nomb_sel == "si") & (dir_sel == "no") & (f12_f3)].nro_devolucion
        list_dir_no_coinc = list_dir_no_coinc.append(list_dir_no_coinc2)
        list_sop_valido = dist_digitadores.loc[(sop_g == "si") & (est_en == "si") & (nomb_sel == "si") & (dir_sel == "si") & (f12_f3)].nro_devolucion
        list_sop_valido2 = dist_digitadores.loc[(sop_g == "no") & (est_en == "na") & (nomb_sel == "si") & (dir_sel == "na") & (f12_f3)].nro_devolucion
        list_sop_valido = list_sop_valido.append(list_sop_valido2)
        list_dev_a_rem = dist_digitadores.loc[(sop_g == "si") & (est_en == "no") & (nomb_sel == "si") & (dir_sel == "si") & (f12_f3)].nro_devolucion
        list_env_en_rut = dist_digitadores.loc[(sop_g == "si") & (est_en == "na") & (nomb_sel == "si") & (dir_sel == "si") & (f12_f3)].nro_devolucion
        list_sop_inv = dist_digitadores.loc[(sop_g == "si")  & ((dir_sel == "si") | (dir_sel == "no")) &  ((est_en == "si") | (est_en == "no")) & ((nomb_sel == "no") | (dist_digitadores.dg_f12_f11_corresponde == "no") | (dist_digitadores.dg_f3_corresponde == "no") | ((dist_digitadores.dg_f12_f11_corresponde == "na") & (dist_digitadores.dg_f3_corresponde == "na"))) ].nro_devolucion
        list_sop_inv2 = dist_digitadores.loc[(sop_g == "no") & (est_en == "na") & ((dir_sel == "si") | (dir_sel == "no")) & ((nomb_sel == "no") | (dist_digitadores.dg_f12_f11_corresponde == "no") | (dist_digitadores.dg_f3_corresponde == "no") | ((dist_digitadores.dg_f12_f11_corresponde == "na") & (dist_digitadores.dg_f3_corresponde == "na"))) ].nro_devolucion
        list_sop_inv = list_sop_inv.append(list_sop_inv2)
        list_sin_sop = dist_digitadores.loc[(sop_g == "na") & (est_en == "na") & (nomb_sel == "na") & (dir_sel == "na") & (dist_digitadores.dg_f12_f11_corresponde == "na") & (dist_digitadores.dg_f3_corresponde == "na")].nro_devolucion

        if len(list_dir_no_coinc) > 0 :
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_dir_no_coinc), "tipificacion_1"] = "Dirección no coincide"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_dir_no_coinc), "decision"] = "En proceso"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_dir_no_coinc), "estado_proceso"] =  "En proceso"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_dir_no_coinc), "responsable_de_gestion"] = "MKP"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_dir_no_coinc), "gestion"] =  "Enviar correo al seller y confirmar que recibido el F12"

        if len(list_sop_valido) > 0 :
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_sop_valido), "tipificacion_1"] = "Soporte válido"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_sop_valido), "decision"] = "Solicitar confirmación"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_sop_valido), "estado_proceso"] =  "Cerrado"
            
        if len(list_sop_inv) > 0 :
            cont = 0
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_sop_inv), "tipificacion_1"] = "Soporte inválido"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_sop_inv), "decision"] = "En proceso"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_sop_inv), "estado_proceso"] =  "En proceso"
            for i in const.locales:
                        dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_sop_inv) & (dist_digitadores.local_agg == i ),"gestion"] = const.gestion[cont]
                        dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_sop_inv) & (dist_digitadores.local_agg == i ),"responsable_de_gestion" ]= i
                        cont=cont+1
                        
        if len(list_sin_sop) > 0 :
            cont = 0
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_sin_sop), "tipificacion_1"] = "Sin soporte"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_sin_sop), "decision"] = "En proceso"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_sin_sop), "estado_proceso"] =  "En proceso"
            for i in const.locales:
                        dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_sin_sop) & (dist_digitadores.local_agg == i ),"gestion"] = const.gestion[cont]
                        dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_sin_sop) & (dist_digitadores.local_agg == i ),"responsable_de_gestion" ]= i
                        cont=cont+1

        if len(list_dev_a_rem) > 0:
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_dev_a_rem), "tipificacion_1"] = "Devuelto a remitente"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_dev_a_rem), "decision"] = "En proceso"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_dev_a_rem), "estado_proceso"] =  "En proceso"
            cont = 0 
            for i in const.locales:
                dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_dev_a_rem) & (dist_digitadores.local_agg == i ),"gestion"] = "ubicar el producto, relacionarlo en el archivo de devoluciones y volverlo a enviar - relacionar el nuevo número de guía"
                dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_dev_a_rem) & (dist_digitadores.local_agg == i ),"responsable_de_gestion" ]= i
                cont=cont+1
                
        if len(list_env_en_rut) > 0:
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_env_en_rut), "tipificacion_1"] = "Envío en ruta"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_env_en_rut), "decision"] = "En proceso"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_env_en_rut), "estado_proceso"] =  "En proceso"
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_env_en_rut), "gestion"] = "Revisar que  la guía no supere 8 días calendario posteriores al envío "
            dist_digitadores.loc[dist_digitadores.nro_devolucion.isin(list_env_en_rut), "responsable_de_gestion" ]= "MKP"

        dist_digitadores.loc[dist_digitadores.tipificacion_1.isna(), "tipificacion_1"] = "Revisar diligenciamiento"
        
        return dist_digitadores

    def save_f3_a_validar(self): # TODO revisar los filtros para la selección de la info 
        path = self.path + "/consolidado/resultado_unificación"   
        validar = self.consolidado.loc[self.consolidado.tipificacion_1 =="Soporte válido",["nro_devolucion","folio_f12","proveedor","rut_proveedor","local","estado_descrip"]] #TODO hay que modificar el filtro.
        validar.to_excel(f"{path}/{self.dt_string}_f3_a_confirmar.xlsx",sheet_name = 'DB', index=False)
        print(f"-- Se guardó el archivo f3 a confirmar ubicación: {path}")

    def calculos_correo(self):
        path = 'python/temp/'
        x_estado_desc= self.planilla.groupby(['estado_descrip']).agg({'cant*costoprmd': 'sum', 'nro_devolucion': 'nunique'}).reset_index()
        x_estado_desc["cant*costoprmd"] = x_estado_desc["cant*costoprmd"]/1e6
        x_estado_desc.to_html(f"{path}/estado_desc.html", index=False, classes='table table-striped',justify="center")
        x_estado_agg = self.planilla.groupby("estado_agg")['cant*costoprmd'].sum().reset_index()
        x_estado_agg['cant*costoprmd'] = x_estado_agg['cant*costoprmd']/1e6
        x_estado_agg.to_html(f"{path}/estado_agg.html", index=False, classes='table table-striped',justify="center")
        x_local_agg =self.planilla.loc[self.planilla.estado_agg == "abierto"]
        x_local_agg = x_local_agg.groupby(["local_agg"]).agg({'cant*costoprmd': 'sum', "nro_devolucion": "nunique"}).reset_index()
        x_local_agg["cant*costoprmd"] = x_local_agg["cant*costoprmd"]/1e6
        x_local_agg.to_html(f"{path}/local_agg.html", index=False, classes='table table-striped',justify="center")
        local_agg= px.bar(x_local_agg, x='local_agg', y= 'cant*costoprmd', title= "Resumen de F3 por local",labels={'local_agg':'Locales','cant*costoprmd':'Valor'},  text='cant*costoprmd') 
        local_agg.write_image(f"{path}/local_agg.jpg")
        estado_agg=px.bar(x_estado_agg, x='estado_agg', y= 'cant*costoprmd', title= "Resumen de F3 por estado agg",labels={'estado_agg':'Estado','cant*costoprmd':'Valor'},  text='cant*costoprmd')
        estado_agg.write_image(f"{path}/estado_agg.jpg")
        estado_desc=px.bar(x_estado_desc, x='estado_descrip', y= 'cant*costoprmd', title= "Resumen de F3 por estado",labels={'estado_descrip':'Estado','cant*costoprmd':'Valor'},  text='cant*costoprmd')
        estado_desc.write_image(f"{path}/estado_desc.jpg")

    def conv_text(self,dist_digitador, op):
        for i in const.cols_a_validar[3:]:
            dist_digitador[f"{i}"] = dist_digitador[f"{i}"].str.strip()
            if op == "low":
                dist_digitador[f"{i}"] = dist_digitador[f"{i}"].str.lower()
            elif op == "upp":
                dist_digitador[f"{i}"] = dist_digitador[f"{i}"].str.upper()
        return dist_digitador