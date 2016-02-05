''' Runs different models to analyze motor data and the brain (vertex based)'''

from scipy import stats
import numpy as np
import statsmodels.api as sm


jdx = 4
jqc = 2
jsex = 5
jage = 10
jscan = 3
jm_raw = [12, 15, 18, 21]
# jm_raw = [21]
jm_std = [13, 16, 19, 22]
# jm_std = [22]
jmed_info = 11
jm_titles = ['MD', 'AC', 'Bal', 'Total']
# jm_titles = ['Total']
abc_file = '/Users/sudregp/Documents/bethany/abc_clean.csv'
vertex_dir = '/Users/sudregp/Documents/bethany/'
# vertex_files = ['lh.thickness.10.mgh', 'rh.thickness.10.mgh']  ,
#                 'lh.volume.10.mgh', 'rh.volume.10.mgh',
#                 'lh.area.10.mgh', 'rh.area.10.mgh']
vertex_files = ['lh.area.10.mgh', 'rh.area.10.mgh']
vertex_files = [fname[:-4] + '_clean.csv' for fname in vertex_files]
qc_thresh = 2  # <=
p_thresh = .01  # <=

###


def printHeader(text):
    print '\n\n%%%%%%%%%%%%%%%%%%%\n'
    print text
    print '\n%%%%%%%%%%%%%%%%%%%\n'


def make_pmap(vertices, motor):
    ''' Vertices is a list, motor is the behavioral variables to look at '''
    num_params = len(vertices[0][0].pvalues) - 1
    tmap = np.empty([len(vertices), num_params])
    for v, vert in enumerate(vertices):
        tmap[v] = vert[motor].pvalues[1:]  # the first one is the slope
    return tmap


print 'Loading data...'
abc = np.recfromtxt(abc_file, delimiter=',')
mdata = np.genfromtxt(abc_file, delimiter=',')
ndata = []
for fname in vertex_files:
    vdata = np.genfromtxt(vertex_dir + fname, delimiter=',')
    ndata.append(vdata[:, 1:])  # the first column has mask IDs
print 'done'

adhd = [i for i, rec in enumerate(abc) if rec[jdx] == 'ADHD' and mdata[i, jqc] <= qc_thresh and rec[jscan] == 1 and rec[jage] >= 4 and rec[jage] <= 12]
nv = [i for i, rec in enumerate(abc) if rec[jdx] == 'NV' and mdata[i, jqc] <= qc_thresh and rec[jscan] == 1 and rec[jage] >= 4 and rec[jage] <= 12]

# Ttest between NV and ADHD, standard motor variables
print 'N: ', len(nv), '(NV),', len(adhd), '(ADHD)'
nvXadhd = []
for midx, m in enumerate(jm_std):
    x = np.delete(mdata[nv, m], np.nonzero(np.isnan(mdata[nv, m]) == True))
    y = np.delete(mdata[adhd, m], np.nonzero(np.isnan(mdata[adhd, m]) == True))
    t, p = stats.ttest_ind(x, y, equal_var=False)
    nvXadhd.append(p)
    print 'T-test NV vs ADHD: std %s = %.4f' % (jm_titles[midx], p)

# Ttest between boys and girld, standard motor variables
boys = [i for i, rec in enumerate(abc) if rec[jsex].lower() == 'm' and mdata[i, jqc] <= qc_thresh and rec[jscan] == 1 and rec[jage] >= 4 and rec[jage] <= 12]
girls = [i for i, rec in enumerate(abc) if rec[jsex].lower() == 'f' and mdata[i, jqc] <= qc_thresh and rec[jscan] == 1 and rec[jage] >= 4 and rec[jage] <= 12]
print 'N: ', len(boys), '(boys),', len(girls), '(girls)'
boysXgirls = []
for midx, m in enumerate(jm_std):
    x = np.delete(mdata[boys, m], np.nonzero(np.isnan(mdata[boys, m]) == True))
    y = np.delete(mdata[girls, m], np.nonzero(np.isnan(mdata[girls, m]) == True))
    t, p = stats.ttest_ind(x, y, equal_var=False)
    boysXgirls.append(p)
    print 'T-test boys vs girls: std %s = %.4f' % (jm_titles[midx], p)

# ANOVA among NV, meds, unmeds
med = [i for i, rec in enumerate(abc) if rec[jdx] == 'ADHD' and mdata[i, jqc] <= qc_thresh and rec[jscan] == 1 and rec[jmed_info].lower() == 'y' and rec[jage] >= 4 and rec[jage] <= 12]
unmed = [i for i, rec in enumerate(abc) if rec[jdx] == 'ADHD' and mdata[i, jqc] <= qc_thresh and rec[jscan] == 1 and rec[jmed_info].lower() == 'n' and rec[jage] >= 4 and rec[jage] <= 12]
print 'N: ', len(nv), '(NV),', len(med), '(med),', len(unmed), '(unmed)'
nvXmeds = []
for midx, m in enumerate(jm_std):
    x = np.delete(mdata[nv, m], np.nonzero(np.isnan(mdata[nv, m]) == True))
    y = np.delete(mdata[med, m], np.nonzero(np.isnan(mdata[med, m]) == True))
    z = np.delete(mdata[unmed, m], np.nonzero(np.isnan(mdata[unmed, m]) == True))
    f, p = stats.f_oneway(x, y, z)
    nvXadhd.append(p)
    print 'ANOVA NV vs med vs unmed: std %s = %.4f' % (jm_titles[midx], p)

# Ttest between all combinations of 3 groups, standard motor variables
print 'N: ', len(nv), '(NV),', len(med), '(med),', len(unmed), '(unmed)'
pairwiseTtests = []
for midx, m in enumerate(jm_std):
    x = np.delete(mdata[nv, m], np.nonzero(np.isnan(mdata[nv, m]) == True))
    y = np.delete(mdata[med, m], np.nonzero(np.isnan(mdata[med, m]) == True))
    t, p = stats.ttest_ind(x, y, equal_var=False)
    pairwiseTtests.append(p)
    print 'T-test NV vs med: std %s = %.4f' % (jm_titles[midx], p)

    x = np.delete(mdata[nv, m], np.nonzero(np.isnan(mdata[nv, m]) == True))
    y = np.delete(mdata[unmed, m], np.nonzero(np.isnan(mdata[unmed, m]) == True))
    t, p = stats.ttest_ind(x, y, equal_var=False)
    pairwiseTtests.append(p)
    print 'T-test NV vs unmed: std %s = %.4f' % (jm_titles[midx], p)

    x = np.delete(mdata[med, m], np.nonzero(np.isnan(mdata[med, m]) == True))
    y = np.delete(mdata[unmed, m], np.nonzero(np.isnan(mdata[unmed, m]) == True))
    t, p = stats.ttest_ind(x, y, equal_var=False)
    pairwiseTtests.append(p)
    print 'T-test med vs unmed: std %s = %.4f' % (jm_titles[midx], p)


good_subjects = nv + adhd
num_subjects = len(good_subjects)

# encoding diagnostic
diag = .5 * np.ones([num_subjects, 1])
for idx, row in enumerate(good_subjects):
    if abc[row][jdx].lower() == 'adhd':
        diag[idx, 0] = -.5

# encoding sex
sex = .5 * np.ones([len(good_subjects), 1])
for idx, row in enumerate(good_subjects):
    if abc[row][jsex].lower() == 'f':
        sex[idx, 0] = -.5

age = np.reshape(mdata[good_subjects, jage], (-1, 1))


#### Different linear models ####

printHeader('y ~ motorBattery')
model = {}
# run models for all vertex tables
for v, vtable in enumerate(ndata):
    print vertex_files[v]
    model[vertex_files[v]] = {}
    # run every possible motor variable
    for mid, m in enumerate(jm_std):
        model[vertex_files[v]][jm_titles[mid]] = {}
        model[vertex_files[v]][jm_titles[mid]]['pvalues'] = []
        model[vertex_files[v]][jm_titles[mid]]['tstats'] = []

        x = mdata[good_subjects, m]
        # model matrix with intercept
        X = sm.add_constant(x)
        # run it for all vertices in this table
        for b in range(vtable.shape[1]):
            y = vtable[good_subjects, b]
            # least squares fit
            fit = sm.OLS(y, X, missing='drop').fit()
            model[vertex_files[v]][jm_titles[mid]]['pvalues'].append(fit.pvalues)
            model[vertex_files[v]][jm_titles[mid]]['tstats'].append(fit.tvalues)
model1 = model


# printHeader('y ~ motorBattery*diagnosis*sex + motorBattery*diagnosis + motorBattery*sex + sex*diagnosis + motorBattery + diagnosis + sex')
# model = {}
# # run models for all vertex tables
# for v, vtable in enumerate(ndata):
#     print vertex_files[v]
#     model[vertex_files[v]] = {}
#     # run every possible motor variable
#     for mid, m in enumerate(jm_std):
#         model[vertex_files[v]][jm_titles[mid]] = {}
#         model[vertex_files[v]][jm_titles[mid]]['pvalues'] = []
#         model[vertex_files[v]][jm_titles[mid]]['tstats'] = []

#         motor = np.reshape(mdata[good_subjects, m], (-1, 1))  # adding another dimension to the vector
#         x = np.hstack([motor * diag * sex, motor * diag, motor * sex,
#                        sex * diag, motor, diag, sex])
#         # model matrix with intercept
#         X = sm.add_constant(x)
#         # run it for all vertices in this table
#         for b in range(vtable.shape[1]):
#             y = vtable[good_subjects, b]
#             # least squares fit
#             fit = sm.OLS(y, X, missing='drop').fit()
#             model[vertex_files[v]][jm_titles[mid]]['pvalues'].append(fit.pvalues)
#             model[vertex_files[v]][jm_titles[mid]]['tstats'].append(fit.tvalues)
# model2 = model


# printHeader('y ~ motorBattery*diagnosis*age + motorBattery*diagnosis + motorBattery*age + age*diagnosis + motorBattery + diagnosis + age')
# model = {}
# # run models for all vertex tables
# for v, vtable in enumerate(ndata):
#     print vertex_files[v]
#     model[vertex_files[v]] = {}
#     # run every possible motor variable
#     for mid, m in enumerate(jm_std):
#         model[vertex_files[v]][jm_titles[mid]] = {}
#         model[vertex_files[v]][jm_titles[mid]]['pvalues'] = []
#         model[vertex_files[v]][jm_titles[mid]]['tstats'] = []

#         motor = np.reshape(mdata[good_subjects, m], (-1, 1))  # adding another dimension to the vector
#         x = np.hstack([motor * diag * age, motor * diag, motor * age,
#                        age * diag, motor, diag, age])
#         # model matrix with intercept
#         X = sm.add_constant(x)
#         # run it for all vertices in this table
#         for b in range(vtable.shape[1]):
#             y = vtable[good_subjects, b]
#             # least squares fit
#             fit = sm.OLS(y, X, missing='drop').fit()
#             model[vertex_files[v]][jm_titles[mid]]['pvalues'].append(fit.pvalues)
#             model[vertex_files[v]][jm_titles[mid]]['tstats'].append(fit.tvalues)
# model3 = model


# printHeader('y ~ motorBattery(raw)*diagnosis*age + motorBattery(raw)*diagnosis + motorBattery(raw)*age + age*diagnosis + motorBattery(raw) + diagnosis + age')
# model = {}
# # run models for all vertex tables
# for v, vtable in enumerate(ndata):
#     print vertex_files[v]
#     model[vertex_files[v]] = {}
#     # run every possible motor variable
#     for mid, m in enumerate(jm_raw):
#         model[vertex_files[v]][jm_titles[mid]] = {}
#         model[vertex_files[v]][jm_titles[mid]]['pvalues'] = []
#         model[vertex_files[v]][jm_titles[mid]]['tstats'] = []

#         motor = np.reshape(mdata[good_subjects, m], (-1, 1))  # adding another dimension to the vector
#         x = np.hstack([motor * diag * age, motor * diag, motor * age,
#                        age * diag, motor, diag, age])
#         # model matrix with intercept
#         X = sm.add_constant(x)
#         # run it for all vertices in this table
#         for b in range(vtable.shape[1]):
#             y = vtable[good_subjects, b]
#             # least squares fit
#             fit = sm.OLS(y, X, missing='drop').fit()
#             model[vertex_files[v]][jm_titles[mid]]['pvalues'].append(fit.pvalues)
#             model[vertex_files[v]][jm_titles[mid]]['tstats'].append(fit.tvalues)
# model4 = model


printHeader('y ~ motorBattery*diagnosis*age + motorBattery(raw)*diagnosis + motorBattery(raw)*age + age*diagnosis + motorBattery(raw) + diagnosis + age')
model = {}
# run models for all vertex tables
for v, vtable in enumerate(ndata):
    print vertex_files[v]
    model[vertex_files[v]] = {}
    # run every possible motor variable
    for mid, m in enumerate(jm_raw):
        model[vertex_files[v]][jm_titles[mid]] = {}
        model[vertex_files[v]][jm_titles[mid]]['pvalues'] = []
        model[vertex_files[v]][jm_titles[mid]]['tstats'] = []

        motor = np.reshape(mdata[good_subjects, m], (-1, 1))  # adding another dimension to the vector
        x = np.hstack([motor * diag * age, motor * diag, motor * age,
                       age * diag, motor, diag, age])
        # model matrix with intercept
        X = sm.add_constant(x)
        # run it for all vertices in this table
        for b in range(vtable.shape[1]):
            y = vtable[good_subjects, b]
            # least squares fit
            fit = sm.OLS(y, X, missing='drop').fit()
            model[vertex_files[v]][jm_titles[mid]]['pvalues'].append(fit.pvalues)
            model[vertex_files[v]][jm_titles[mid]]['tstats'].append(fit.tvalues)
model5 = model

'''
printHeader('y ~ motorBattery + diagnosis + motorBattery * diagnosis')
for mid, m in enumerate(m_std):
    for b in range(1, ndata.shape[1]):
        motor = np.reshape(mdata[:, m], (-1, 1))  # adding another dimension to the vector
        x = np.hstack([motor, diag, motor * diag])
        y = ndata[:, b]
        # model matrix with intercept
        X = sm.add_constant(x)
        # least squares fit
        model = sm.OLS(y, X, missing='drop')
        fit = model.fit()
        if np.any(fit.pvalues[1:] <= p_thresh):
            print 'Combination', m_titles[mid], 'and', n_titles[b-1]
            print fit.summary()

printHeader('y ~ motorBattery(raw) + diagnosis + motorBattery(raw) * diagnosis + age * diagnosis')
age = np.reshape(mdata[:, age_idx], (-1, 1))
for mid, m in enumerate(m_raw):
    for b in range(1, ndata.shape[1]):
        motor = np.reshape(mdata[:, m], (-1, 1))  # adding another dimension to the vector
        x = np.hstack([motor, diag, motor * diag, age * diag])
        y = ndata[:, b]
        # model matrix with intercept
        X = sm.add_constant(x)
        # least squares fit
        model = sm.OLS(y, X, missing='drop')
        fit = model.fit()
        if np.any(fit.pvalues[1:] <= p_thresh):
            print 'Combination', m_titles[mid], 'and', n_titles[b-1]
            print fit.summary()

printHeader('y ~ motorBattery(raw) + diagnosis + motorBattery(raw) * diagnosis + age')
age = np.reshape(mdata[:, age_idx], (-1, 1))
for mid, m in enumerate(m_raw):
    for b in range(1, ndata.shape[1]):
        motor = np.reshape(mdata[:, m], (-1, 1))  # adding another dimension to the vector
        x = np.hstack([motor, diag, motor * diag, age])
        y = ndata[:, b]
        # model matrix with intercept
        X = sm.add_constant(x)
        # least squares fit
        model = sm.OLS(y, X, missing='drop')
        fit = model.fit()
        if np.any(fit.pvalues[1:] <= p_thresh):
            print 'Combination', m_titles[mid], 'and', n_titles[b-1]
            print fit.summary()

printHeader('y ~ motorBattery + diagnosis + motorBattery * diagnosis + age * diagnosis')
age = np.reshape(mdata[:, age_idx], (-1, 1))
for mid, m in enumerate(m_std):
    for b in range(1, ndata.shape[1]):
        motor = np.reshape(mdata[:, m], (-1, 1))  # adding another dimension to the vector
        x = np.hstack([motor, diag, motor * diag, age * diag])
        y = ndata[:, b]
        # model matrix with intercept
        X = sm.add_constant(x)
        # least squares fit
        model = sm.OLS(y, X, missing='drop')
        fit = model.fit()
        if np.any(fit.pvalues[1:] <= p_thresh):
            print 'Combination', m_titles[mid], 'and', n_titles[b-1]
            print fit.summary()

printHeader('y ~ motorBattery + diagnosis + motorBattery * diagnosis + age')
age = np.reshape(mdata[:, age_idx], (-1, 1))
for mid, m in enumerate(m_std):
    for b in range(1, ndata.shape[1]):
        motor = np.reshape(mdata[:, m], (-1, 1))  # adding another dimension to the vector
        x = np.hstack([motor, diag, motor * diag, age])
        y = ndata[:, b]
        # model matrix with intercept
        X = sm.add_constant(x)
        # least squares fit
        model = sm.OLS(y, X, missing='drop')
        fit = model.fit()
        if np.any(fit.pvalues[1:] <= p_thresh):
            print 'Combination', m_titles[mid], 'and', n_titles[b-1]
            print fit.summary()

printHeader('y ~ motorBattery + diagnosis + motorBattery * diagnosis + sex * diagnosis')
for mid, m in enumerate(m_std):
    for b in range(1, ndata.shape[1]):
        motor = np.reshape(mdata[:, m], (-1, 1))  # adding another dimension to the vector
        x = np.hstack([motor, diag, motor * diag, sex * diag])
        y = ndata[:, b]
        # model matrix with intercept
        X = sm.add_constant(x)
        # least squares fit
        model = sm.OLS(y, X, missing='drop')
        fit = model.fit()
        if np.any(fit.pvalues[1:] <= p_thresh):
            print 'Combination', m_titles[mid], 'and', n_titles[b-1]
            print fit.summary()
'''