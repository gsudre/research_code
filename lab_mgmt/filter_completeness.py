import numpy as np

fname = '/Users/sudregp/tmp/completenessUpTo12132013.txt'
dates = {'IQ': [14, 15, 16, 20, 21], 'ClinicalInterview': [17, 18, 19]}  
test_names = {'IQ': ['WPPSI-III', 'WASI-II', 'WASI-I', 'WTAR', 'WPPSI-IV'],
              'ClinicalInterview': ['SCID', 'DICA', 'CAADID']}

# figure out the last column that has data to be copied without cleaning
last_data = np.min([np.min(col) for col in dates.itervalues()])
clean_data = []
data = np.recfromtxt(fname, delimiter='\t')
maskids = np.unique([rec[0] for rec in data])
for m in maskids:
    mask_data = []
    # finds all rows for this specific mask id
    rows = [i for i in range(len(data)) if data[i][0]==m]
    mask_data.append(list(data[rows[0]][:last_data]))
    # NEED TO DO ALL THE FILTERING NECESSARY TO ACQUIRE LAST DATE FOR CLINICAL INTERVIES AND IQ TESTS

    clean_data.append(mask_data)
# WRITE TO BIG LIST TO CSV FILE
