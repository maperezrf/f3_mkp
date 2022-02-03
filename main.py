from sqlalchemy import false
from python.f3_mkp import F3MKP
import python.constants as const
from datetime import datetime
import python.llave.bot_keys as bot_keys
from python.bot_teams import BotKatherine
from python.adm_email import EMAILHANDLER # TODO llamar la clase 
import os
os.system("cls")
dt_string = datetime.now().strftime('%y%m%d')

print('Bienvenido a F3 Marketplace:')

f3mkp = F3MKP()
cont = False
# Inicia menu de división de planilla
def menu_distribucion ():
    digitadores = const.get_digitadores()
    digitadoreslist ={}
    print('## Menú de distribución ----- \n  1. Trabajar con todos los digitadores \n  2. Seleccionar algunos digitadores \n  3. Volver')
    opc = int(input('  ++ In: Seleccione la opción que desea realizar: '))

    if opc == 1 : 
        f3mkp.build_consolidado()
        f3mkp.div_planilla()
    elif opc == 2:
        menu_start = "s"
        while menu_start == "s":
            for i in digitadores:
                print(i,"-",digitadores[i])
            nro_dig= int(input("    ++ In: Seleccione el digitador con el que desea trabajar: "))
            digitadoreslist[nro_dig]=digitadores[nro_dig]
            for i in digitadoreslist:
                print(i,"-",digitadoreslist[i])  
            cont = input("    ++ In: ¿Desea seleccionar otro digitador? S/N: ")
            cont=cont.lower()
            if cont == "n":
                f3mkp.build_consolidado()
                f3mkp.div_planilla(list(digitadoreslist.values()))
                menu_start="n"
            elif cont =="s":
                continue
            else: 
                print("    -- Out: Opción no valida")   
    elif opc==3:
        pass
    else:
        print('    -- Out: Ingrese una opción valida (1-3)')

def menu_general():
    menu_start=True
    while menu_start == True:
        digitadores = const.get_digitadores()
        selection = ''
        print('  ## Menú -----------------')
        print('  1. Distribuir registros \n  2. Unificar registros \n  3. BOT Katherine \n  4. Generar planilla F3 \n  5. Enviar correo \n  6. Configuraciones \n  0. Salir')
        selection = input('++ In: Por favor digite una opción: ')
        if selection == '1':
            menu_distribucion()
        elif selection=='2':
            folder = input('  0-Volver\n Ingrese nombre de carpeta: ' )
            if folder != "0":
                nc_df = f3mkp.unir_planillas_d(folder)
                indice_si_cambio=f3mkp.compare_dfs(nc_df)
                if len(indice_si_cambio) > 0:
                    f3mkp.disponibilizar_no_gest(indice_si_cambio)
                    nc_df = f3mkp.conv_text(nc_df,"low")
                    nc_df_validados = f3mkp.validate_df(indice_si_cambio,nc_df)
                    nc_df_validados = f3mkp.conv_text(nc_df_validados,"upp")
                    f3mkp.agregar_gestionados(indice_si_cambio, nc_df_validados)
                    f3mkp.save_f3_a_validar()
                    f3mkp.guardar_consolidado()
            else:
                pass 
            # f3mkp.validate_df(df)
        elif selection== '3':
            # Bot message sending
            bot = BotKatherine(bot_keys.urlkatherine)  # Inicializa conexión con bot
            f3mkp.build_planilla()
            planilla = f3mkp.get_planilla()
            gb_estado = planilla.groupby('estado').agg({'cant*costoprmd': 'sum', 'nro_devolucion': 'nunique'})
            gb_estado_agg = planilla.groupby(["estado_agg"]).agg({'cant*costoprmd': 'sum', "nro_devolucion": "nunique"})
            costo_t = (planilla['cant*costoprmd'].sum()/1e6)  # Costo total
            bot.send_msg(gb_estado_agg, gb_estado, costo_t)
        elif selection=='4':
            f3mkp.build_planilla()
            planilla = f3mkp.get_planilla()
            path = f'output/planillas/{dt_string}_F3_MKP.xlsx'
            planilla.to_excel(path, index=False)  # Database saving
            print('# Output: --------------------------------------------------------------')
            print(f'La planilla fue guardada en: {path} \n')
        elif selection == '5':
            f3mkp.build_planilla()
            f3mkp.calculos_correo()
            email = EMAILHANDLER()
            mensaje = email.header_email()
            html = email.body()
            email.build_body(html,mensaje)
            email.send_email(mensaje)
            print ("-------**** El correo fue enviado exitosamente ****-------------")        
        elif selection == '6': #TODO pasar a metodos.
            digitadores = const.get_digitadores()
            print("  *** Listado de digitadores actual ***")
            cant_dig = len(digitadores)
            if  cant_dig == 0:
                print("  -- Out: El listado de digitadores está vacío ")
            else:
                for i in digitadores:
                    print(f"    {i} - {digitadores[i]}")
            print("  ## Menú de configuración -----")
            print("    1- Agregar digitadores")
            print("    2- Borrar todos los digitadores")
            print("    3- Eliminar digitadores")
            print("    4- Volver")
            opc = int(input("    ++ In: Seleccione la opción que desea realizar: "))

            path_digitadores = 'python/config/digitadores.txt'
            if opc == 1:
                menua = True
                while menua == True:
                    nombre = input(f"    ++ In: Ingrese el nombre del digitador que desea adicionar: ")
                    archivo = open(path_digitadores,"a")
                    with open(path_digitadores, "a") as archivo:
                        nombre = nombre.lower()
                        nombre = nombre.title()
                        nombre = nombre.strip()
                        archivo.write(f"{nombre},")    
                        archivo.close()                    
                    res = input("    ++ In: Desea agregar a otro digitador? S/N:")
                    res = res.lower()
                    if res == "s":
                        pass
                    elif res == "n":
                        menua = False
                    else:
                        print("Opción no valida") 
            elif opc == 2:
                menub =True
                while menub == True:
                    res = input(" - ¿Está seguro de borrar el listado de digitadores? S/N:")
                    res.lower()
                    if res == "s":
                        with open(path_digitadores, "r+") as archivo:
                            archivo.truncate(0)
                            archivo.close()
                        menub = False
                    elif res == "n":
                        menub = False
                    else:
                        print("    --- Opción no valida") 
            elif opc == 3: 
                menu = True
                while menu == True:
                    dig = int(input("Ingrese el número del digitador a eliminar"))
                    del digitadores[dig]
                    res = input("Desea eliminar a otro digitador? S/N")
                    res = res.lower() 
                    if res == "s":
                        pass
                    if res == "n":
                        menu = False
                nuevo_listado=[]
                for i in digitadores:
                    nuevo_listado.append(f"{digitadores[i]},")
                with open(path_digitadores, "w") as archivo:
                    for i in nuevo_listado:
                        archivo.write(i)
                    archivo.close()
            elif opc == 4:
                pass

        elif selection == '0':
            menu_start=False
            #os.system("cls") # TODO revisar si eliminar
        else: 
            print('Ingrese una opción valida (0-5)')

menu_general()



