import BCRPclient as BCRP
import matplotlib.pyplot as plt 

# import pandas
banc = BCRP.Marco()

banc.get_metadata()
# banc.load_metadata()

print(banc.metadata)

banc.query()
banc.query('PN00015MM')

# banc.codigos = ['PN01288PM','PN01289PM']
# banc.ref_metadata('metadata_refined.csv')







# banc.codigos = ['PN01288PM','PN01289PM','PN00015MM']
# banc.fechaini = '2020-1'
# banc.fechafin = '2023-1'

# banc.state_inputs()

# df = banc.GET('GET.csv')



# for name in df.columns:
#     plt.figure(figsize=(9, 4))

#     banc.plot(df[name],name,'plot')
#     plt.show()
# plt.show()