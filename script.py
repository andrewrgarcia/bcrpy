import BCRPclient as BCRP
import matplotlib.pyplot as plt 
import numpy as np
# import pandas
banc = BCRP.Marco()

# banc.get_metadata()
banc.load_metadata()

print(banc.metadata)

# banc.query()
# banc.query('PN00015MM')

# banc.codigos = ['PN01288PM','PN01289PM']
# banc.ref_metadata('metadata_refined.csv')



# print(BCRP.Levenshtein(banc.metadata, 'estadisticas'))

# banc.metadata=banc.metadata.drop([2,3])
# banc.metadata=banc.metadata.drop([6,9])
# print(banc.metadata)


# banc.wordsearch('economia')
banc.wordsearch('economia',columnas =[0,1])

# print(df.shape)
# print(df.iloc[[0,11]] )
# df= banc.metadata
# for i in df.index :
#     print(i)

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