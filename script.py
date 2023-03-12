import BCRPclient as BCRP

info = BCRP.Marco()

# info.get_metadata()
info.load_metadata()

print(info.metadata)

info.query()
info.query('PN00015MM')

info.codigos = ['PD39793AM','PN00015MM', 'PN00015MM']

info.refine('metadata_refined.csv')