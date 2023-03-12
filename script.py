import BCRPclient as BCRP

import pandas
dis = BCRP.Marco()

dis.get_metadata()
# dis.load_metadata()

# print(dis.metadata)

# dis.consulta()
# dis.consulta('PN00015MM')

# dis.codigos = ['PN01288PM','PN01289PM']
# dis.ref_metadata('metadata_refined.csv')

# '''https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01288PM-PN01289PM/\
# grafico/2010-1/2016-9/esp'''  # TEMPLATE


# dis.load_metadata()
# dis.idioma = 'esp'
# dis.codigos = ['PN01288PM','PN01289PM','PN00015MM']

# dis.state_inputs()

# df = dis.GET('GET.csv')
