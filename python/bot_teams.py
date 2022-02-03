import pymsteams 
from datetime import datetime
# inicia canal del bot

class BotKatherine():

    supportsFiles:True
    dt = datetime.now().strftime('%d-%m-%Y')    

    def __init__(self, url) -> None:
        self.myTeamsMessage = pymsteams.connectorcard(url, verify=False)

    def send_msg(self, cxe, sxe, costo_total):
        # cxe: cantidad_x_extado
        # puk: puk df 
        # sxe: calculos_x_estado
        self.myTeamsMessage.title("RESUMEN - F3 MARKETPLACE 2021")
        self.myTeamsMessage.text(f"Fecha:{self.dt}")

        #seccion1
        seccion1 = pymsteams.cardsection()
        seccion1.title ("RESUMEN F3 ABIERTOS")
        seccion1.addFact("Costo F3 abiertos: ",f"{(cxe['cant*costoprmd'][0]/1e6):,.0f} M")
        seccion1.addFact("Cantidad F3 abiertos: ",f"{(cxe['nro_devolucion'][0]):,.0f}")
        #myMessageSection.addImage('https://i.pinimg.com/564x/d4/b6/35/d4b63562285a2c5264a2002fa72646fd.jpg', ititle="This Is Fine")

        #seccion2
        seccion2 = pymsteams.cardsection()
        seccion2.title ("RESUMEN F3 GLOBAL")
        seccion2.addFact("Costo total: ",f"{costo_total:,.0f} M")
        seccion2.addFact("Confirmado: ",f"{(sxe['cant*costoprmd'][1]/1e6):,.0f} M")
        seccion2.addFact("Anulado: ",f"{(sxe['cant*costoprmd'][0]/1e6):,.0f} M")
        seccion2.addFact("Enviado: ",f"{(sxe['cant*costoprmd'][2]/1e6):,.0f} M")
        seccion2.addFact("Reservado: ",f"{(sxe['cant*costoprmd'][3]/1e6):,.0f} M")
        #seccion2.addImage('https://i.pinimg.com/564x/d4/b6/35/d4b63562285a2c5264a2002fa72646fd.jpg', ititle="This Is Fine")
        self.myTeamsMessage.addSection(seccion2)
        self.myTeamsMessage.addSection(seccion1)
        self.myTeamsMessage.printme ()
        self.myTeamsMessage.send()