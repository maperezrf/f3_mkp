tienda = ['101', '108', '93', '6', '183', '25', '38', '53', '13', '43', '82',
         '138', '72', '35', '60', '123', '98', '36', '19', '18', '50', '45',
         '85', '56', '96','322', '131', '139', '141', '143', '5', '142', '37','3009', '30']
cd = [  '3000', '9903', '2000', '2001', '2002', '9970', '9901', '3002', '9905', '9961', '5']
sac = [ '3001','99']
nan = ['11','9910','3004','3006','9902', '9921','9951']
#digitadores = {1:"Claudia",2:"Gerardo",3:"Jefferson",4:"Jessica",5:"Karen",6:"Martha",7:"Tania",8:"Yuly"}
# digitadores = {1:"Angie",2:"Miguel",3:"Pablo"}

def get_digitadores(): # TODO cambiar lugar, poner en otro archivo, unificar con el resto de métodos de digitores
       path_digitadores = 'python/config/digitadores.txt'
       dic_digitadores={}
       with open(path_digitadores, "r") as tf:
              lines = tf.read().split(',')
       for i in enumerate(lines):
              if i[0] != len(lines)-1:
                     dic_digitadores[i[0]+1] = i[1]
              else:
                     pass
       tf.close()    
       return dic_digitadores

cols_a_validar=['indice_f3','fecha_sconfirmacion', 'digitador_responsable',  
       'dg_soporte_guia_transp',
       'dg_entregado_guia_plataf_transp', 'dg_seller_en_destinatario',
       'dg_direccion_seller', 'dg_f12_f11_corresponde', 'dg_f3_corresponde', 'novedad']

cols_a_agregar = ["tipificacion_1","tipificacion_2","tipificacion_3","responsable_de_gestion","gestion","decision","estado_proceso"]

consolidado_cols = ['nro_devolucion', 'Fecha Revisión ', 'Fecha SConfirmación', 'Responsable', 'Soporte es una guía de transportadora?', 
'N° GUÍA / \nCARTA CAMBIO', 'Estado entregado de gúia en la plataforma de la transportadora?','Nombre del seller en el destinatario?',
'Dirección del seller corresponde?', 'F12 corresponde?','F3 corresponde?', 'Tipificación 1', 'Tipificación 2','Gestión para MKP ', 
'Gestión para Tienda', 'Gestión para SAC','Gestión para CD', 'Decisión', 'ESTADO_PROCESO', 'Novedad',  'upc', 'sku']

cols_consolidado=['nro_devolucion', 'fecha_reserva','dg_fecha_revision','fecha_sconfirmacion', 'digitador_responsable',  
       'dg_soporte_guia_transp','dg_n_guia/_carta_cambio', 'dg_transportadora',
       'dg_entregado_guia_plataf_transp', 'dg_seller_en_destinatario',
       'dg_direccion_seller', 'dg_f12_f11_corresponde', 'dg_f3_corresponde', 'novedad',
       'tipificacion_1', 'tipificacion_2', 'tipificacion_3', 'responsable_de_gestion', 'gestion', 
       'decision', 'estado_proceso', 'usr_validacion', 'entregado_a_adm', 'fecha_envio', 'fecha_confirmacion', 'fecha_anulacion', 
       'upc', 'sku', 'descripcion', 'marca', 'proveedor', 'rut_proveedor', 
       'local', 'local_descrip', 'local_agg', 'duplicado', 'estado_descrip', 'estado_agg', 'cantidad', 'cant*costoprmd',
       'tipo_documento_para_dev', 'nc_proveedor', 'folio_f11', 'folio_f12', 'usuario_creacion','dup_f3']

cols_para_digitador = ['indice_f3','nro_devolucion', 'fecha_reserva','dg_fecha_revision','fecha_sconfirmacion', 'digitador_responsable',  
       'dg_soporte_guia_transp','dg_n_guia/_carta_cambio', 'dg_transportadora',
       'dg_entregado_guia_plataf_transp', 'dg_seller_en_destinatario', 
       'dg_direccion_seller', 'dg_f12_f11_corresponde', 'dg_f3_corresponde', 'novedad', 
       'upc', 'sku', 'descripcion', 'marca', 
       'proveedor', 'rut_proveedor','estado_descrip',
       'local', 'local_descrip', 'local_agg', 'cantidad', 'cant*costoprmd',
       'tipo_documento_para_dev',
       'folio_f11', 'folio_f12']

cols_a_incoporar_consolidado_a_planilla = [
'nro_devolucion', 'upc', 'cantidad', 
'dg_fecha_revision',
 'fecha_sconfirmacion',
 'digitador_responsable',
 'dg_soporte_guia_transp',
'dg_n_guia/_carta_cambio',
 'dg_transportadora',
 'dg_entregado_guia_plataf_transp',
 'dg_seller_en_destinatario',
 'dg_direccion_seller',
 'dg_f12_f11_corresponde',
 'dg_f3_corresponde',
 'novedad',
 'tipificacion_1',
 'tipificacion_2',
 'tipificacion_3',
 'responsable_de_gestion',
 'gestion',
 'decision',
 'estado_proceso',
 'usr_validacion',
 'entregado_a_adm',
 ]

locales=['CD','TIENDA','SAC']

gestion=['Buscar guía y relacionarlo en el archivo','Buscar guía y relacionar el # de guía "planilla no mix"','Buscar guía y relacionarla en el drive ']

