# -*- coding : utf-8 -*-
# Tim @ MIT sloan - tianyil@mit.edu
# version: May.25, 2020
# Tim @ CUHK DSE - tianyi.li@cuhk.edu.hk
# version: Jan.18, 2022


import os
import time
import csv
import codecs 
import pandas as pd
import numpy as np
import scipy as sp
from scipy import signal
import subprocess
import sys

def func_Run_command(cmd, max_repeat,out_file_name): 
 
    '''run cmd, wait timeout seconds per trial. Max trial is max_repeat '''
    
    repeat = 0
    end_flag = 0
    
    while True:
    
        time.sleep(1)
        
        proc = subprocess.Popen(cmd) # stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True
        repeat = repeat + 1
        t_start = time.time()  
        
        while True:  
            if proc.poll() == 0:    # process end normally 
                end_flag = 1
                break 
            
            if timeout_trial and time.time() - t_start > timeout_trial:  
                if proc.poll() is not None and proc.poll() != 0:
                    proc.terminate()  
                    proc.kill()
                    end_flag = 0
                    break
            
            if timeout_run and time.time() - t_start > timeout_run:  
                proc.terminate()  
                proc.kill()
                end_flag = 0
                break
                
        if (not os.path.exists(out_file_name)) or end_flag == 0:
            print('Run command Failed. Trial ' + str(repeat) +'/' + str(max_repeat) +' .\n')
            end_flag = 0
        
        if end_flag == 1:
            break    
            
        time.sleep(timeout_trial)
        
        if repeat+1 > max_repeat:
            print('ERROR: All run command trials Failed! \n')
            sys.exit(0)

def func_Edit_cin():

    ''' Edit the cin file for the estimation model '''
    ''' modify the simulation TIME STEP in estimation '''

    f = open(S2_cin_name,'r')
    lines = f.readlines()
    f.close()
    
    for j in range(len(lines)):
        if 'TIME STEP' in lines[j]:
            lines[j] = 'TIME STEP = ' + str(est_time_step) +' \n'
        if 'IV for SEIR' in lines[j]:
            lines[j] = 'IV for SEIR = ' + str(IV_for_SEIR) +' \n'
        if 'IV for Noise' in lines[j]:
            lines[j] = 'IV for Noise = ' + str(IV_for_Noise) +' \n'
        if 'Min Variance F' in lines[j]:           
            lines[j] = 'Min Variance F = ' + str(min_variance_F) +' \n'
            
    f = open(S2_cin_name,'w')
    f.writelines(lines)
    f.close()
    
def func_Edit_vpd(method,cal_type):

    ''' Edit the vpd file for the given method '''
    ''' cal_type pool : ['E','I','R','I+R'] '''
    
    if method[0:2] == 'na':
    
        if 'mcmc' not in method:
            method = 'naive'
        else:
            method = 'naive_mcmc'
            
    if method[0:5] == 'mcmc-':
        method = 'mcmc'
    if 'kf' in method:
        if 'mcmc' in method:
            method = 'mcmc_kf'
        else:
            method = 'kf'
      
    vpd_name_out = 'payoff_' + str(method) +'.vpd'

    new_lines = []
    
    if method == 'mcmc':
    
        if trans == 'Y' and vpd_type == 'G':
            new_lines.append('*PL\n')
        else:
            new_lines.append('*P\n')
            
        if cal_type == ['E','I','R']:
            temp_mcmc = 'EIR'
        if cal_type == ['I','R']:
            temp_mcmc = 'IR'
        if cal_type == ['I']:
            temp_mcmc = 'I'      

        mcmc_vpd_type = [vpd_type][0]
        
        if vpd_type == 'G' and var_scaling == 'Y':
            mcmc_vpd_type = 'S'

        new_lines.append(vpd_FS + ' MCMC payoff ' + mcmc_vpd_type + ' ' + temp_mcmc + '/-1\n')
        
    elif 'naive' in method:
                
        if vpd_type == 'G':
        
            if trans == 'N':
                new_lines.append('*CG\n')
            else:
                new_lines.append('*CGL\n')
                
            if 'E' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Exposure Rate|Exposure Rate Data/Exposure Rate DATA STD' + (var_scaling == 'Y')*' Scaled' + '\n')
                if vpd_FS == 'S':
                    new_lines.append('EXPOSED|Exposed Data/EXPOSED DATA STD' + (var_scaling == 'Y')*' Scaled' + '\n')
            if 'I' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Infection Rate|Infection Rate Data/Infection Rate DATA STD' + (var_scaling == 'Y')*' Scaled' + '\n')
                if vpd_FS == 'S':
                    new_lines.append('INFECTED|Infected Data/INFECTED DATA STD' + (var_scaling == 'Y')*' Scaled' + '\n')
            if 'R' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Recovery Rate|Recovery Rate Data/Recovery Rate DATA STD' + (var_scaling == 'Y')*' Scaled' + '\n')
                if vpd_FS == 'S':
                    new_lines.append('RECOVERED|Recovered Data/RECOVERED DATA STD' + (var_scaling == 'Y')*' Scaled' + '\n')
            if 'I+R' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Infection Rate|Infection Rate Data/Infection Rate DATA STD' + (var_scaling == 'Y')*' Scaled' + '\n')
                if vpd_FS == 'S':
                    new_lines.append('INFECTED RECOVERED|Infected Recovered Data/INFECTED RECOVERED DATA STD' + (var_scaling == 'Y')*' Scaled' + '\n')
                
        if vpd_type == 'P':
        
            new_lines.append('*CP\n')

            if 'E' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Exposure Rate|Exposure Rate Data/1\n')
                if vpd_FS == 'S':
                    new_lines.append('EXPOSED|Exposed Data/1\n')
            if 'I' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Infection Rate|Infection Rate Data/1\n')
                if vpd_FS == 'S':
                    new_lines.append('INFECTED|Infected Data/1\n')
            if 'R' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Recovery Rate|Recovery Rate Data/1\n')
                if vpd_FS == 'S':
                    new_lines.append('RECOVERED|Recovered Data/1\n')
            if 'I+R' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Infection Rate|Infection Rate Data/1\n')
                if vpd_FS == 'S':
                    new_lines.append('INFECTED RECOVERED|Infected Recovered Data/1\n')

        if vpd_type == 'B':
        
            new_lines.append('*CB\n')
            
            if 'E' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Exposure Rate|Exposure Rate Data/1\n')
                if vpd_FS == 'S':
                    new_lines.append('EXPOSED|Exposed Data/1\n')
            if 'I' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Infection Rate|Infection Rate Data/1\n')
                if vpd_FS == 'S':
                    new_lines.append('INFECTED|Infected Data/1\n')
            if 'R' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Recovery Rate|Recovery Rate Data/1\n')
                if vpd_FS == 'S':
                    new_lines.append('RECOVERED|Recovered Data/1\n')
            if 'I+R' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Infection Rate|Infection Rate Data/1\n')
                if vpd_FS == 'S':
                    new_lines.append('INFECTED RECOVERED|Infected Recovered Data/1\n')
        
        if vpd_type == 'NB':
                 
            new_lines.append('*P\n')
                
            if cal_type == ['E','I','R']:
                temp_mcmc = 'EIR'
            if cal_type == ['I','R']:
                temp_mcmc = 'IR'
            if cal_type == ['I']:
                temp_mcmc = 'I'                
            new_lines.append(vpd_FS + ' NB Payoff ' + temp_mcmc + '/1\n')   # Note: the weight is 1 here, compared with -1 for MCMC
        

        if 'mcmc' in method:
        
            if trans == 'Y' and vpd_type == 'G':
                new_lines.append('*PL\n')
            else:
                new_lines.append('*P\n')
                
            if cal_type == ['E','I','R']:
                temp_mcmc = 'EIR'
            if cal_type == ['I','R']:
                temp_mcmc = 'IR'
            if cal_type == ['I']:
                temp_mcmc = 'I'          

            mcmc_vpd_type = [vpd_type][0]
        
            if vpd_type == 'G' and var_scaling == 'Y':
                mcmc_vpd_type = 'S'
            
            new_lines.append(vpd_FS + ' MCMC payoff ' + mcmc_vpd_type + ' ' + temp_mcmc + '/-1\n')
            
    else:
       
        if 'kf' in method:
        
            new_lines.append('*CK\n')
            if 'E' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Exposure Rate|Exposure Rate Data/Exposure Rate DATA Variance' + (var_scaling == 'Y')*' Scaled' + '\n')
                if vpd_FS == 'S':
                    new_lines.append('EXPOSED|Exposed Data/EXPOSED DATA VARIANCE' + (var_scaling == 'Y')*' Scaled' + '\n')
            if 'I' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Infection Rate|Infection Rate Data/Infection Rate DATA Variance' + (var_scaling == 'Y')*' Scaled' + '\n')
                if vpd_FS == 'S':
                    new_lines.append('INFECTED|Infected Data/INFECTED DATA VARIANCE' + (var_scaling == 'Y')*' Scaled' + '\n')
            if 'R' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Recovery Rate|Recovery Rate Data/Recovery Rate DATA Variance' + (var_scaling == 'Y')*' Scaled' + '\n')
                if vpd_FS == 'S':
                    new_lines.append('RECOVERED|Recovered Data/RECOVERED DATA VARIANCE' + (var_scaling == 'Y')*' Scaled' + '\n')
            if 'I+R' in cal_type:
                if vpd_FS == 'F':
                    new_lines.append('Infection Rate|Infection Rate Data/Infection Rate DATA Variance' + (var_scaling == 'Y')*' Scaled' + '\n')
                if vpd_FS == 'S':
                    new_lines.append('INFECTED RECOVERED|Infected Recovered Data/INFECTED RECOVERED DATA VARIANCE' + (var_scaling == 'Y')*' Scaled' + '\n')
                    
        #if 'mcmc' in method:
        #
        #    if trans == 'Y' and vpd_type == 'G':
        #        new_lines.append('*PL\n')
        #    else:
        #        new_lines.append('*P\n')
        #        
        #    if cal_type == ['E','I','R']:
        #        temp_mcmc = 'EIR'
        #    if cal_type == ['I','R']:
        #        temp_mcmc = 'IR'
        #    if cal_type == ['I']:
        #        temp_mcmc = 'I'         

        #    mcmc_vpd_type = [vpd_type][0]
        
        #    if vpd_type == 'G' and var_scaling == 'Y':
        #        mcmc_vpd_type = 'S'
        #    
        #    new_lines.append(vpd_FS + ' MCMC payoff ' + mcmc_vpd_type + ' ' + temp_mcmc + '/-1\n')

    f = open(vpd_name_out,'w')
    f.writelines(new_lines)
    f.close()

def func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter):

    ''' Edit the voc file for the given method '''
    ''' According to (global) optimization parameters '''
    
    if method[0:2] == 'na':
    
        if 'mcmc' not in method:
            method = 'naive'
        else:
            method = 'naive_mcmc'
        
    if method[0:5] == 'mcmc-':
        method = 'mcmc'
    if 'kf' in method:
        if 'mcmc' in method:
            method = 'mcmc_kf'
        else:
            method = 'kf'
     
    
    voc_name_full = 'opt_full_' + str(method) +'.voc'
    voc_name_out = 'opt_' + str(method) +'.voc'

    f = open(voc_name_full,'r')
    lines = f.readlines()
    f.close()
    
    new_lines = []
    for i in range(len(lines)):
        if lines[i][0] == ':':
        
            # edit specific clause #
            if 'RESTART_MAX' in lines[i]:
                lines[i] = ':RESTART_MAX=' + str(restart_max) + '\n'
            if 'MCLIMIT' in lines[i]:
                lines[i] = ':MCLIMIT=' + str(mcmc_limit) + '\n'
            if 'MCBURNIN' in lines[i]:
                lines[i] = ':MCBURNIN=' + str(mcmc_burnin) + '\n'
            if 'MAX_ITERATIONS' in lines[i]:
                lines[i] = ':MAX_ITERATIONS=' + str(max_iter) + '\n'
            if 'MCPAYOFFTYPE' in lines[i]:
                lines[i] = ':MCPAYOFFTYPE=0' + '\n'
                
            new_lines.append(lines[i])

    if 'kf' in method:
        if kf_opt == 'W':
            temp_num_para = min(4,num_para)
        if kf_opt == 'P':
            temp_num_para = min(5,num_para)                            ## n_R
    else:
        if vpd_type in ['G','N']:
            temp_num_para = min(4,num_para)                            ## powell/MCMC-related methods can invert one scale of noise when using Gaussian payoff
        else:
            temp_num_para = min(3,num_para)                            ## Poisson (or Binomal payoff) cannot invert scale of noise
        
    for j in range(temp_num_para):
        temp = str(range_para[j][0]) + '<=' + name_para[j] + ' =' + \
            str(range_para[j][1]) + '<=' + str(range_para[j][2]) + '\n'
        new_lines.append(temp)
    
    if method not in ['kf','kf_mcmc','mcmc_kf'] and vpd_type == 'NB':  ## Negative Binomal payoff can invert r
    
        temp = str(range_para[num_para-1][0]) + '<=' + name_para[num_para-1] + ' =' + \
            str(range_para[num_para-1][1]) + '<=' + str(range_para[num_para-1][2]) + '\n'
        new_lines.append(temp)

    if 'kf' in method and kf_opt == 'P':                               ## KFA/KFSA can invert Noise correlation time
        
        temp = str(range_para[num_para][0]) + '<=' + name_para[num_para] + ' =' + \
            str(range_para[num_para][1]) + '<=' + str(range_para[num_para][2]) + '\n'
        new_lines.append(temp)
        
    f = open(voc_name_out,'w')
    f.writelines(new_lines)
    f.close()
    
def func_SG_filtering():

    ''' Savitzky-Golay filtering: edit the data.csv file '''

    filename = 'data.csv'
    data = pd.read_csv(filename)

    data_name = ['Exposed Data','Infected Data','Recovered Data']
    for i in range(3):
        ind = [k for k in range(len(data)) if data.iloc[k,0] == data_name[i]]

        x = np.array(data.iloc[ind,1:])
        y = sp.signal.savgol_filter(x, 5, 2)
        data.iloc[ind,1:] = y

    filename = 'data_sg.csv'
    data.to_csv(filename,index=False)

def func_Estimation(method,cmd_file_name,out_file_name,result_matrix,extra_matrix,iter_ind,SG_switch):

    ''' Estimation methods: naive/kf/mcmc/mcmc_kf '''
    ''' Return the result matrix of estimated optima '''
    ''' For MCMC based methods, also return a tab file '''
    
    # choose vdf/model #
    f = open(cmd_file_name,'r')
    lines = f.readlines()
    f.close()
    
    for j in range(len(lines)):
        if 'SIMULATE>DATA' in lines[j]:
            if SG_switch == 0:
                lines[j] = 'SIMULATE>DATA|data.vdfx' +'\n'
            else:
                lines[j] = 'SIMULATE>DATA|data_sg.vdfx' +'\n'
                
        if 'SIMULATE>RUNNAME' in lines[j]:
            lines[j] = 'SIMULATE>RUNNAME|' + method + '.vdfx' +'\n'
        
        if 'kf' in method:
            if 'SPECIAL>LOADMODEL' in lines[j]:
                if kf_opt == 'W':
                    lines[j] = 'SPECIAL>LOADMODEL|STD_SEIR_estimation.mdl' + '\n'
                if kf_opt == 'P':
                    lines[j] = 'SPECIAL>LOADMODEL|STD_SEIR_estimation_p.mdl' + '\n'

    f = open(cmd_file_name,'w')
    f.writelines(lines)
    f.close()
    
    # edit kalman.prm #
    
    if os.path.exists('kalman.prm'):
        os.remove('kalman.prm')
        
    if kf_opt == 'W':
        f = open('kalman_w.prm','r')
        lines = f.readlines()
        f.close()
    if kf_opt == 'P':    
        f = open('kalman_p.prm','r')
        lines = f.readlines()
        f.close()

    f = open('kalman.prm','w')
    f.writelines(lines)
    f.close()
    
    # estimation #
    
    if os.path.exists(out_file_name):
        os.remove(out_file_name)
    script_path = script_path_0 + cmd_file_name
    cmd = vensim_path + " \"" + script_path + "\""
    func_Run_command(cmd, max_repeat,out_file_name)

    time.sleep(1)
    
    f = open(out_file_name,'r')
    lines = f.readlines()
    f.close()
    
    for i in range(len(lines)):  # find the end of commands -- row end_row #
        if ':COMSYS After' in lines[i]:
            ind1 = [a for (a,b) in enumerate(list(lines[i])) if b == ' '][1]
            ind2 = [a for (a,b) in enumerate(list(lines[i])) if b == ' '][2]
            result_matrix[iter_ind][0] = float(lines[i][ind1+1:ind2])
        if ':COMSYS Best payoff is' in lines[i]:
            result_matrix[iter_ind][1] = float(lines[i][23:])
        if ':COMSYS Too many Iterations. Optimization not complete' in lines[i]:
            print('Error! Possiblity: Random Start too large for KF.')
            time.sleep(1)
        if lines[i][0] != ':':
            break
            
    end_row = i
    
    for j in range(num_para):
        
        if j + end_row < len(lines):
            ind1 = [a for (a,b) in enumerate(list(lines[j+end_row])) if b == '='][1]
            ind2 = [a for (a,b) in enumerate(list(lines[j+end_row])) if b == '='][2]
            result_matrix[iter_ind][j+2] = float(lines[j+end_row][ind1+1:ind2-1])
        else:
            result_matrix[iter_ind][j+2] = 0
            
    if 'mcmc' in method:
    
        tab_file_name = method + '_MCMC_sample.tab'
        extra_matrix = func_Calculate_MCMC(tab_file_name,extra_matrix,iter_ind)
        
    return result_matrix,extra_matrix 
       
def func_Calculate_MCMC(tab_file_name,extra_matrix,iter_ind):

    ''' Calculate statistics (25 properties) for MCMC results '''
    
    f = open(tab_file_name,'r')
    lines = f.readlines()
    f.close()
    
    lines = lines[1:]

    value_matrix = [[[12345] for col in range(num_para)] for row in range(len(lines))]

    for i in range(len(lines)):
        ind = [a for (a,b) in enumerate(list(lines[i])) if b == '\t']
        ind = [-1] + ind
        
        for j in range(num_para):
            if j + 2 > len(ind):
                value_matrix[i][j] = 0
            else:
                value_matrix[i][j] = float(lines[i][ind[j]+1:ind[j+1]])

    # statistics #
    
    for j in range(num_para):        
        value_col = [value_matrix[k][j] for k in range(len(value_matrix))]
        
        if len(value_col) == 0:
            first_7 = [0]*7
            next_25 = [0]*2*len(percentile_list)
            print('Failed Iteration. Continue.')
        else:
            first_7 = [len(value_col),min(value_col),max(value_col),np.mean(value_col),
                np.median(value_col),np.std(value_col),np.std(value_col)/max(np.mean(value_col),1e-6)]
            
            next_25 = []
            
            for q in range(len(percentile_list)):
            
                lower_p = np.percentile(value_col, percentile_list[q][0])
                upper_p = np.percentile(value_col, percentile_list[q][1])
                next_25.append(lower_p)
                next_25.append(upper_p)
        
        extra_matrix[iter_ind][j*statistics_item:(j+1)*statistics_item] = first_7 + next_25
        
    return extra_matrix
      
def func_Write_output(method,result_matrix,extra_matrix):

    ''' Write output for each estimation method as a separate csv '''
    ''' For MCMC based methods, output an extra csv '''
    
    f = open(output_file_name + method + '.csv','w',newline='')
    writer = csv.writer(f)
    for i in range(iter_time):
        row = result_matrix[i][:]
        writer.writerow(row)
    f.close()
    
    if 'naive' not in method:
        f = open(output_file_name + method + '_extra.csv','w',newline='')
        writer = csv.writer(f)
        for i in range(iter_time):
            row = extra_matrix[i][:]
            writer.writerow(row)
        f.close()

def func_Write_info(stage_ind):

    ''' Write parameter info for a specific run '''

    f = open(output_file_name + 'info.txt','w')
    f.write('*******Parameter Info*******\n')
    f.write('****************************\n')
    f.write('*********Stage Index********\n')
    f.write('-----> ' + stage_ind)
    f.write('\n')
    f.write('[iter_time]\n')
    f.write(str(iter_time))
    f.write('\n')
    f.write('[num_para]\n')
    f.write(str(num_para))
    f.write('\n')
    f.write('[name_para]\n')
    f.write(str(name_para))
    f.write('\n')
    f.write('[range_para]\n')
    f.write(str(range_para))
    f.write('\n')
    f.write('[restart_max]\n')
    f.write(str(restart_max))
    f.write('\n')
    f.write('[mcmc_limit]\n')
    f.write(str(mcmc_limit))
    f.write('\n')
    f.write('[mcmc_burnin]\n')
    f.write(str(mcmc_burnin))
    f.write('\n')
    f.write('[max_iter]\n')
    f.write(str(max_iter))
    f.write('\n')
    f.write('[cal_type]\n')
    f.write(str(cal_type))
    f.write('\n')
    f.write('[est_time_step]\n')
    f.write(str(est_time_step))
    f.write('\n')
    f.write('[min_variance_F]\n')
    f.write(str(min_variance_F))
    f.write('\n')
    f.write('[min_variance_F_2]\n')
    f.write(str(min_variance_F_2))
    f.write('\n')
    f.write('[IV_for_SEIR]\n')
    f.write(str(IV_for_SEIR))
    f.write('\n')
    f.write('[IV_for_Noise]\n')
    f.write(str(IV_for_Noise))
    f.write('\n')
    f.write('[noise_1]\n')
    f.write(str(noise_1))
    f.write('\n')
    f.write('[noise_2]\n')
    f.write(str(noise_2))
    f.write('\n')
    f.write('[noise_corr_time]\n')
    f.write(str(noise_corr_time))
    f.write('\n')
    f.write('[noise_corr_time_rob]\n')
    f.write(str(noise_corr_time_rob))
    f.write('\n')
    f.write('[vpd_type]\n')
    f.write(str(vpd_type))
    f.write('\n')
    f.write('[trans]\n')
    f.write(str(trans))
    f.write('\n')
    f.write('[var_scaling]\n')
    f.write(str(var_scaling))
    f.write('\n')
    f.write('[vpd_FS]\n')
    f.write(str(vpd_FS))
    f.write('\n')
    f.write('[kf_opt]\n')
    f.write(str(kf_opt))
    f.write('\n')
    f.write('[timeout_trial]\n')
    f.write(str(timeout_trial))
    f.write('\n')
    f.write('[timeout_run]\n')
    f.write(str(timeout_run))
    f.write('\n')
    f.write('[max_repeat]\n')
    f.write(str(max_repeat))
    f.write('\n')
    f.write('[STD_flag]\n')
    f.write(str(STD_flag))
    f.write('\n')
    
    f.close()
    
################################################################################################

#### Main ####

from params import *

global iter_time,percentile_list,statistics_item,name_para,num_para,range_para,restart_max,mcmc_limit,mcmc_burnin,max_iter,cal_type,vpd_FS,kf_opt,est_time_step,min_variance_F,IV_for_SEIR,IV_for_Noise,noise_1,noise_2,noise_corr_time,vpd_type,trans,var_scaling
global timestamp,S1_cin_name,S2_cin_name,vensim_path,script_path_0,timeout_trial,timeout_run,max_repeat,output_file_name

start_time = time.time()

if run_s1_mcmc_flag == 1:

    ## Iteration - mcmc ##

    cal_type = ['E','I','R']

    result_mcmc_G = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_P = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_NB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_GL = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_GS = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]

    extra_mcmc_G = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_P = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_NB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_GL = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_GS = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]

    print('[@][RUN -- LIKELIHOOD -- powell]')
    print('[@]Start. Total Iteration: ' + str(iter_time))

    func_Edit_cin()

    #start_time = time.time()

    for i in range(iter_time):

        ## Step 1 - Data Generation ##
        
        f = open(S1_cin_name,'r')
        lines = f.readlines()
        f.close()
        
        for j in range(len(lines)):
            if 'seed' in lines[j]:
                lines[j] = 'random seed = ' + str((i+1)*100) +' \n'
            if 'Noise correlation time' in lines[j]:
                lines[j] = 'Noise correlation time = ' + str(noise_corr_time) +' \n'
            if 'Noise Amp ED' in lines[j]:
                lines[j] = 'Noise Amp ED = ' + str(noise_1) +' \n'
            if 'Noise Amp ID' in lines[j]:
                lines[j] = 'Noise Amp ID = ' + str(noise_1) +' \n'
            if 'Noise Amp RD' in lines[j]:
                lines[j] = 'Noise Amp RD = ' + str(noise_1) +' \n'
            if 'Noise Amp ER' in lines[j]:
                lines[j] = 'Noise Amp ER = ' + str(noise_1) +' \n'
            if 'Noise Amp IR' in lines[j]:
                lines[j] = 'Noise Amp IR = ' + str(noise_1) +' \n'
            if 'Noise Amp RR' in lines[j]:
                lines[j] = 'Noise Amp RR = ' + str(noise_1) +' \n'
        f = open(S1_cin_name,'w')
        f.writelines(lines)
        f.close()
        
        temp_output_name = 'data.vdfx'
        if os.path.exists(temp_output_name):
            os.remove(temp_output_name)
        script_path = script_path_0 + cmd_file_name_d
        cmd = vensim_path + " \"" + script_path + "\""
        func_Run_command(cmd, max_repeat,temp_output_name)
        time.sleep(1)

        ## Step 2 - Estimation ##
       
        if scheme_flag[0] == 1:
            # mcmc-G #
            mcmc_limit = mcmc_limit_pool[0]               
            mcmc_burnin = mcmc_limit - 1000 
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N' 
            var_scaling = 'N'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_G, extra_mcmc_G = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_G,extra_mcmc_G,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[1] == 1:
            # mcmc-P #
            mcmc_limit = mcmc_limit_pool[1]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'P'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_P, extra_mcmc_P = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_P,extra_mcmc_P,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[2] == 1:
            # mcmc-NB #
            mcmc_limit = mcmc_limit_pool[2]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'NB'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_NB, extra_mcmc_NB = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_NB,extra_mcmc_NB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[3] == 1:
            # mcmc-GL #
            mcmc_limit = mcmc_limit_pool[3]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'Y' 
            var_scaling = 'N'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_GL, extra_mcmc_GL = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_GL,extra_mcmc_GL,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[4] == 1:
            # mcmc-GS #
            mcmc_limit = mcmc_limit_pool[4]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_GS, extra_mcmc_GS = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_GS,extra_mcmc_GS,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        print('Success -- Iteration: '+ str(i+1) + '/' + str(iter_time) +  ' -- Time Elapsed:' + str(time.time()-start_time) + ' s')

    print('[@]End. Writing output file...')

    ## Output ##

    output_file_name = 'output/o_' + str(int(time.time())) + '_'

    # 1 - mcmc-G
    method = 'G'
    func_Write_output(method,result_mcmc_G,extra_mcmc_G)
    # 2 - mcmc-P
    method = 'P'
    func_Write_output(method,result_mcmc_P,extra_mcmc_P)
    # 3 - mcmc-NB
    method = 'NB'
    func_Write_output(method,result_mcmc_NB,extra_mcmc_NB)
    # 4 - mcmc-GL
    method = 'GL'
    func_Write_output(method,result_mcmc_GL,extra_mcmc_GL)
    # 5 - mcmc-GS
    method = 'GS'
    func_Write_output(method,result_mcmc_GS,extra_mcmc_GS)

    # write parameter info #
    func_Write_info('Stage 1')

    print('[@]Output file written. S1 - MCMC')

if run_s1_naive_flag == 1:

    ## Iteration - naive ##

    cal_type = ['E','I','R']

    result_naive_G = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_naive_P = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_naive_NB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_naive_GL = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_naive_GS = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]

    print('[@][RUN -- LIKELIHOOD -- powell]')
    print('[@]Start. Total Iteration: ' + str(iter_time))

    func_Edit_cin()

    #start_time = time.time()

    for i in range(iter_time):

        ## Step 1 - Data Generation ##
        
        f = open(S1_cin_name,'r')
        lines = f.readlines()
        f.close()
        
        for j in range(len(lines)):
            if 'seed' in lines[j]:
                lines[j] = 'random seed = ' + str((i+1)*100) +' \n'
            if 'Noise correlation time' in lines[j]:
                lines[j] = 'Noise correlation time = ' + str(noise_corr_time) +' \n'
            if 'Noise Amp ED' in lines[j]:
                lines[j] = 'Noise Amp ED = ' + str(noise_1) +' \n'
            if 'Noise Amp ID' in lines[j]:
                lines[j] = 'Noise Amp ID = ' + str(noise_1) +' \n'
            if 'Noise Amp RD' in lines[j]:
                lines[j] = 'Noise Amp RD = ' + str(noise_1) +' \n'
            if 'Noise Amp ER' in lines[j]:
                lines[j] = 'Noise Amp ER = ' + str(noise_1) +' \n'
            if 'Noise Amp IR' in lines[j]:
                lines[j] = 'Noise Amp IR = ' + str(noise_1) +' \n'
            if 'Noise Amp RR' in lines[j]:
                lines[j] = 'Noise Amp RR = ' + str(noise_1) +' \n'
        f = open(S1_cin_name,'w')
        f.writelines(lines)
        f.close()
        
        temp_output_name = 'data.vdfx'
        if os.path.exists(temp_output_name):
            os.remove(temp_output_name)
        script_path = script_path_0 + cmd_file_name_d
        cmd = vensim_path + " \"" + script_path + "\""
        func_Run_command(cmd, max_repeat,temp_output_name)
        time.sleep(1)

        ## Step 2 - Estimation ##
        
        if scheme_flag[0] == 1:
            # naive-G #
            mcmc_limit = mcmc_limit_pool[0]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'naive-G'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'N'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_naive_G, _ = func_Estimation(method,cmd_file_name1,method + '.out',result_naive_G,[],i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[1] == 1:
            # naive-P #
            mcmc_limit = mcmc_limit_pool[1]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'naive-P'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'P'
            trans = 'N'
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_naive_P, _ = func_Estimation(method,cmd_file_name1,method + '.out',result_naive_P,[],i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[2] == 1:
            # naive-NB #
            mcmc_limit = mcmc_limit_pool[2]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'naive-NB'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'NB'
            trans = 'N'
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_naive_NB, _ = func_Estimation(method,cmd_file_name1,method + '.out',result_naive_NB,[],i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[3] == 1:
            # naive-GL #
            mcmc_limit = mcmc_limit_pool[3]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'naive-GL'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'Y'
            var_scaling = 'N'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_naive_GL, _ = func_Estimation(method,cmd_file_name1,method + '.out',result_naive_GL,[],i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[4] == 1:
            # naive-GS #
            mcmc_limit = mcmc_limit_pool[4]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'naive-GS'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_naive_GS, _ = func_Estimation(method,cmd_file_name1,method + '.out',result_naive_GS,[],i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        print('Success -- Iteration: '+ str(i+1) + '/' + str(iter_time) +  ' -- Time Elapsed:' + str(time.time()-start_time) + ' s')

    print('[@]End. Writing output file...')

    ## Output ##

    output_file_name = 'output/o_' + str(int(time.time())) + '_'

    # 1 - naive-G
    method = 'naive-G'
    func_Write_output(method,result_naive_G,[])
    # 2 - naive-P
    method = 'naive-P'
    func_Write_output(method,result_naive_P,[])
    # 3 - naive-NB
    method = 'naive-NB'
    func_Write_output(method,result_naive_NB,[])
    # 4 - naive-GL
    method = 'naive-GL'
    func_Write_output(method,result_naive_GL,[])
    # 5 - naive-GS
    method = 'naive-GS'
    func_Write_output(method,result_naive_GS,[])

    # write parameter info #
    func_Write_info('Stage 1 Naive')

    print('[@]Output file written. S1 - Naive')

if run_s2_flag == 1:

    ## Iteration - KF ##

    cal_type = ['E','I','R']

    result_mcmc_KFB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFA = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSA = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]

    extra_mcmc_KFB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFA = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSA = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]

    print('[@][RUN -- SCHEME]')
    print('[@]Start. Total Iteration: ' + str(iter_time))

    func_Edit_cin()

    #start_time = time.time()

    for i in range(iter_time):

        ## Step 1 - Data Generation ##
        
        f = open(S1_cin_name,'r')
        lines = f.readlines()
        f.close()
        
        for j in range(len(lines)):
            if 'seed' in lines[j]:
                lines[j] = 'random seed = ' + str((i+1)*100) +' \n'
            if 'Noise correlation time' in lines[j]:
                lines[j] = 'Noise correlation time = ' + str(noise_corr_time) +' \n'
            if 'Noise Amp ED' in lines[j]:
                lines[j] = 'Noise Amp ED = ' + str(noise_1) +' \n'
            if 'Noise Amp ID' in lines[j]:
                lines[j] = 'Noise Amp ID = ' + str(noise_1) +' \n'
            if 'Noise Amp RD' in lines[j]:
                lines[j] = 'Noise Amp RD = ' + str(noise_1) +' \n'
            if 'Noise Amp ER' in lines[j]:
                lines[j] = 'Noise Amp ER = ' + str(noise_1) +' \n'
            if 'Noise Amp IR' in lines[j]:
                lines[j] = 'Noise Amp IR = ' + str(noise_1) +' \n'
            if 'Noise Amp RR' in lines[j]:
                lines[j] = 'Noise Amp RR = ' + str(noise_1) +' \n'
        f = open(S1_cin_name,'w')
        f.writelines(lines)
        f.close()
        
        temp_output_name = 'data.vdfx'
        if os.path.exists(temp_output_name):
            os.remove(temp_output_name)
        script_path = script_path_0 + cmd_file_name_d
        cmd = vensim_path + " \"" + script_path + "\""
        func_Run_command(cmd, max_repeat,temp_output_name)
        time.sleep(1)


        ## Step 2 - Estimation ##
        
        if scheme_flag[7] == 1:
            # MKF - W #
            mcmc_limit = mcmc_limit_pool[7]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfw'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'N'
            kf_opt = 'W'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFB, extra_mcmc_KFB = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFB,extra_mcmc_KFB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[8] == 1:
            # MKFS - W #
            mcmc_limit = mcmc_limit_pool[8]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsw'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'W'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSB, extra_mcmc_KFSB = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSB,extra_mcmc_KFSB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[5] == 1:
            # MKF - P #
            mcmc_limit = mcmc_limit_pool[5]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfp'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'N'
            kf_opt = 'P'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFA, extra_mcmc_KFA = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFA,extra_mcmc_KFA,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[6] == 1:
            # MKFS - P #
            mcmc_limit = mcmc_limit_pool[6]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsp'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'P'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSA, extra_mcmc_KFSA = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSA,extra_mcmc_KFSA,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        print('Success -- Iteration: '+ str(i+1) + '/' + str(iter_time) +  ' -- Time Elapsed:' + str(time.time()-start_time) + ' s')

    print('[@]End. Writing output file...')

    ## Output ##

    output_file_name = 'output/o_' + str(int(time.time())) + '_'

    # 1 - MKFW
    method = 'KFB'
    func_Write_output(method,result_mcmc_KFB,extra_mcmc_KFB)
    # 2 - MKFSW
    method = 'KFSB'
    func_Write_output(method,result_mcmc_KFSB,extra_mcmc_KFSB)
    # 3 - MKFP
    method = 'KFA'
    func_Write_output(method,result_mcmc_KFA,extra_mcmc_KFA)
    # 4 - MKFSP
    method = 'KFSA'
    func_Write_output(method,result_mcmc_KFSA,extra_mcmc_KFSA)

    # write parameter info #
    func_Write_info('Stage 2')

    print('[@]Output file written. S2 - KF')

if run_s3_1_flag == 1:

    ## Iteration - 1 ##

    cal_type = ['I','R']

    result_mcmc_NB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_GS = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSA = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]

    extra_mcmc_NB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_GS = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSA = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]

    print('[@][RUN -- LIKELIHOOD -- powell]')
    print('[@]Start. Total Iteration: ' + str(iter_time))

    func_Edit_cin()

    #start_time = time.time()

    for i in range(iter_time):

        ## Step 1 - Data Generation ##
        
        f = open(S1_cin_name,'r')
        lines = f.readlines()
        f.close()
        
        for j in range(len(lines)):
            if 'seed' in lines[j]:
                lines[j] = 'random seed = ' + str((i+1)*100) +' \n'
            if 'Noise correlation time' in lines[j]:
                lines[j] = 'Noise correlation time = ' + str(noise_corr_time) +' \n'
            if 'Noise Amp ED' in lines[j]:
                lines[j] = 'Noise Amp ED = ' + str(noise_1) +' \n'
            if 'Noise Amp ID' in lines[j]:
                lines[j] = 'Noise Amp ID = ' + str(noise_1) +' \n'
            if 'Noise Amp RD' in lines[j]:
                lines[j] = 'Noise Amp RD = ' + str(noise_1) +' \n'
            if 'Noise Amp ER' in lines[j]:
                lines[j] = 'Noise Amp ER = ' + str(noise_1) +' \n'
            if 'Noise Amp IR' in lines[j]:
                lines[j] = 'Noise Amp IR = ' + str(noise_1) +' \n'
            if 'Noise Amp RR' in lines[j]:
                lines[j] = 'Noise Amp RR = ' + str(noise_1) +' \n'
        f = open(S1_cin_name,'w')
        f.writelines(lines)
        f.close()
        
        temp_output_name = 'data.vdfx'
        if os.path.exists(temp_output_name):
            os.remove(temp_output_name)
        script_path = script_path_0 + cmd_file_name_d
        cmd = vensim_path + " \"" + script_path + "\""
        func_Run_command(cmd, max_repeat,temp_output_name)
        time.sleep(1)

        ## Step 2 - Estimation ##
        
        if scheme_flag[2] == 1:
            # mcmc-NB #
            mcmc_limit = mcmc_limit_pool[2]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'NB'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_NB, extra_mcmc_NB = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_NB,extra_mcmc_NB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[4] == 1:
            # mcmc-GS #
            mcmc_limit = mcmc_limit_pool[4]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_GS, extra_mcmc_GS = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_GS,extra_mcmc_GS,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[8] == 1:
            # MKFS - W #
            mcmc_limit = mcmc_limit_pool[8]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsw'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'W'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSB, extra_mcmc_KFSB = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSB,extra_mcmc_KFSB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[6] == 1:
            # MKFS - P #
            mcmc_limit = mcmc_limit_pool[6]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsp'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'P'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSA, extra_mcmc_KFSA = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSA,extra_mcmc_KFSA,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        print('Success -- Iteration: '+ str(i+1) + '/' + str(iter_time) +  ' -- Time Elapsed:' + str(time.time()-start_time) + ' s')

    print('[@]End. Writing output file...')

    ## Output ##

    output_file_name = 'output/o_' + str(int(time.time())) + '_'

    # 1 - mcmc-NB
    method = 'NB'
    func_Write_output(method,result_mcmc_NB,extra_mcmc_NB)
    # 2 - mcmc-GS
    method = 'GS'
    func_Write_output(method,result_mcmc_GS,extra_mcmc_GS)
    # 3 - MKFSW
    method = 'KFSB'
    func_Write_output(method,result_mcmc_KFSB,extra_mcmc_KFSB)
    # 4 - MKFSP
    method = 'KFSA'
    func_Write_output(method,result_mcmc_KFSA,extra_mcmc_KFSA)

    # write parameter info #
    func_Write_info('Stage 3A')

    print('[@]Output file written. S3 - IR')
    
if run_s3_2_flag == 1:

    ## Iteration - 2 ##

    cal_type = ['I']

    result_mcmc_NB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_GS = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSA = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]

    extra_mcmc_NB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_GS = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSA = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]

    print('[@][RUN -- LIKELIHOOD -- powell]')
    print('[@]Start. Total Iteration: ' + str(iter_time))

    func_Edit_cin()

    #start_time = time.time()

    for i in range(iter_time):

        ## Step 1 - Data Generation ##
        
        f = open(S1_cin_name,'r')
        lines = f.readlines()
        f.close()
        
        for j in range(len(lines)):
            if 'seed' in lines[j]:
                lines[j] = 'random seed = ' + str((i+1)*100) +' \n'
            if 'Noise correlation time' in lines[j]:
                lines[j] = 'Noise correlation time = ' + str(noise_corr_time) +' \n'
            if 'Noise Amp ED' in lines[j]:
                lines[j] = 'Noise Amp ED = ' + str(noise_1) +' \n'
            if 'Noise Amp ID' in lines[j]:
                lines[j] = 'Noise Amp ID = ' + str(noise_1) +' \n'
            if 'Noise Amp RD' in lines[j]:
                lines[j] = 'Noise Amp RD = ' + str(noise_1) +' \n'
            if 'Noise Amp ER' in lines[j]:
                lines[j] = 'Noise Amp ER = ' + str(noise_1) +' \n'
            if 'Noise Amp IR' in lines[j]:
                lines[j] = 'Noise Amp IR = ' + str(noise_1) +' \n'
            if 'Noise Amp RR' in lines[j]:
                lines[j] = 'Noise Amp RR = ' + str(noise_1) +' \n'
        f = open(S1_cin_name,'w')
        f.writelines(lines)
        f.close()
        
        temp_output_name = 'data.vdfx'
        if os.path.exists(temp_output_name):
            os.remove(temp_output_name)
        script_path = script_path_0 + cmd_file_name_d
        cmd = vensim_path + " \"" + script_path + "\""
        func_Run_command(cmd, max_repeat,temp_output_name)
        time.sleep(1)

        ## Step 2 - Estimation ##
        
        if scheme_flag[2] == 1:
            # mcmc-NB #
            mcmc_limit = mcmc_limit_pool[2]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'NB'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_NB, extra_mcmc_NB = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_NB,extra_mcmc_NB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[4] == 1:
            # mcmc-GS #
            mcmc_limit = mcmc_limit_pool[4]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_GS, extra_mcmc_GS = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_GS,extra_mcmc_GS,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[8] == 1:
            # MKFS - W #
            mcmc_limit = mcmc_limit_pool[8]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsw'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'W'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSB, extra_mcmc_KFSB = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSB,extra_mcmc_KFSB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[6] == 1:
            # MKFS - P #
            mcmc_limit = mcmc_limit_pool[6]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsp'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'P'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSA, extra_mcmc_KFSA = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSA,extra_mcmc_KFSA,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        print('Success -- Iteration: '+ str(i+1) + '/' + str(iter_time) +  ' -- Time Elapsed:' + str(time.time()-start_time) + ' s')

    print('[@]End. Writing output file...')

    ## Output ##

    output_file_name = 'output/o_' + str(int(time.time())) + '_'

    # 1 - mcmc-NB
    method = 'NB'
    func_Write_output(method,result_mcmc_NB,extra_mcmc_NB)
    # 2 - mcmc-GS
    method = 'GS'
    func_Write_output(method,result_mcmc_GS,extra_mcmc_GS)
    # 3 - MKFSW
    method = 'KFSB'
    func_Write_output(method,result_mcmc_KFSB,extra_mcmc_KFSB)
    # 4 - MKFSP
    method = 'KFSA'
    func_Write_output(method,result_mcmc_KFSA,extra_mcmc_KFSA)

    # write parameter info #
    func_Write_info('Stage 3B')

    print('[@]Output file written. S3 - I')
    
if run_s4_flag == 1:

    ## Iteration ##

    cal_type = ['I','R']

    min_variance_F = min_variance_F_2
    
    result_mcmc_NB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_GS = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSA = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]

    extra_mcmc_NB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_GS = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSA = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]

    print('[@][RUN -- LIKELIHOOD -- powell]')
    print('[@]Start. Total Iteration: ' + str(iter_time))

    func_Edit_cin()

    #start_time = time.time()

    for i in range(iter_time):

        ## Step 1 - Data Generation ##
        
        f = open(S1_cin_name,'r')
        lines = f.readlines()
        f.close()
        
        for j in range(len(lines)):
            if 'seed' in lines[j]:
                lines[j] = 'random seed = ' + str((i+1)*100) +' \n'
            if 'Noise correlation time' in lines[j]:
                lines[j] = 'Noise correlation time = ' + str(noise_corr_time) +' \n'
            if 'Noise Amp ED' in lines[j]:
                lines[j] = 'Noise Amp ED = ' + str(noise_2) +' \n'
            if 'Noise Amp ID' in lines[j]:
                lines[j] = 'Noise Amp ID = ' + str(noise_2) +' \n'
            if 'Noise Amp RD' in lines[j]:
                lines[j] = 'Noise Amp RD = ' + str(noise_2) +' \n'
            if 'Noise Amp ER' in lines[j]:
                lines[j] = 'Noise Amp ER = ' + str(noise_2) +' \n'
            if 'Noise Amp IR' in lines[j]:
                lines[j] = 'Noise Amp IR = ' + str(noise_2) +' \n'
            if 'Noise Amp RR' in lines[j]:
                lines[j] = 'Noise Amp RR = ' + str(noise_2) +' \n'
        f = open(S1_cin_name,'w')
        f.writelines(lines)
        f.close()
        
        temp_output_name = 'data.vdfx'
        if os.path.exists(temp_output_name):
            os.remove(temp_output_name)
        script_path = script_path_0 + cmd_file_name_d
        cmd = vensim_path + " \"" + script_path + "\""
        func_Run_command(cmd, max_repeat,temp_output_name)
        time.sleep(1)

        ## Step 2 - Estimation ##
        
        if scheme_flag[2] == 1:
            # mcmc-NB #
            mcmc_limit = mcmc_limit_pool[2]               
            mcmc_burnin = mcmc_limit - 1000               
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'NB'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_NB, extra_mcmc_NB = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_NB,extra_mcmc_NB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[4] == 1:
            # mcmc-GS #
            mcmc_limit = mcmc_limit_pool[4]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_GS, extra_mcmc_GS = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_GS,extra_mcmc_GS,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[8] == 1:
            # MKFS - W #
            mcmc_limit = mcmc_limit_pool[8]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsw'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'W'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSB, extra_mcmc_KFSB = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSB,extra_mcmc_KFSB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[6] == 1:
            # MKFS - P #
            mcmc_limit = mcmc_limit_pool[6]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsp'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'P'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSA, extra_mcmc_KFSA = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSA,extra_mcmc_KFSA,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        print('Success -- Iteration: '+ str(i+1) + '/' + str(iter_time) +  ' -- Time Elapsed:' + str(time.time()-start_time) + ' s')

    print('[@]End. Writing output file...')

    ## Output ##

    output_file_name = 'output/o_' + str(int(time.time())) + '_'

    # 1 - NB
    method = 'NB'
    func_Write_output(method,result_mcmc_NB,extra_mcmc_NB)
    # 2 - GS
    method = 'GS'
    func_Write_output(method,result_mcmc_GS,extra_mcmc_GS)
    # 3 - MKFSW
    method = 'KFSB'
    func_Write_output(method,result_mcmc_KFSB,extra_mcmc_KFSB)
    # 4 - MKFSP
    method = 'KFSA'
    func_Write_output(method,result_mcmc_KFSA,extra_mcmc_KFSA)

    # write parameter info #
    func_Write_info('Stage 4 Main')

    print('[@]Output file written. S4 - main')

if run_s4_noisetime_flag == 1:

    ## Iteration - 1 ##

    cal_type = ['I','R']
    noise_corr_time = noise_corr_time_rob[1]
    
    min_variance_F = min_variance_F_2

    result_mcmc_NB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_GS = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSA = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]

    extra_mcmc_NB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_GS = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSA = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]

    print('[@][RUN -- LIKELIHOOD -- powell]')
    print('[@]Start. Total Iteration: ' + str(iter_time))

    func_Edit_cin()

    #start_time = time.time()

    for i in range(iter_time):

        ## Step 1 - Data Generation ##
        
        f = open(S1_cin_name,'r')
        lines = f.readlines()
        f.close()
        
        for j in range(len(lines)):
            if 'seed' in lines[j]:
                lines[j] = 'random seed = ' + str((i+1)*100) +' \n'
            if 'Noise correlation time' in lines[j]:
                lines[j] = 'Noise correlation time = ' + str(noise_corr_time) +' \n'
            if 'Noise Amp ED' in lines[j]:
                lines[j] = 'Noise Amp ED = ' + str(noise_2) +' \n'
            if 'Noise Amp ID' in lines[j]:
                lines[j] = 'Noise Amp ID = ' + str(noise_2) +' \n'
            if 'Noise Amp RD' in lines[j]:
                lines[j] = 'Noise Amp RD = ' + str(noise_2) +' \n'
            if 'Noise Amp ER' in lines[j]:
                lines[j] = 'Noise Amp ER = ' + str(noise_2) +' \n'
            if 'Noise Amp IR' in lines[j]:
                lines[j] = 'Noise Amp IR = ' + str(noise_2) +' \n'
            if 'Noise Amp RR' in lines[j]:
                lines[j] = 'Noise Amp RR = ' + str(noise_2) +' \n'
        f = open(S1_cin_name,'w')
        f.writelines(lines)
        f.close()
        
        temp_output_name = 'data.vdfx'
        if os.path.exists(temp_output_name):
            os.remove(temp_output_name)
        script_path = script_path_0 + cmd_file_name_d
        cmd = vensim_path + " \"" + script_path + "\""
        func_Run_command(cmd, max_repeat,temp_output_name)
        time.sleep(1)

        ## Step 2 - Estimation ##
        
        if scheme_flag[2] == 1:
            # mcmc-NB #
            mcmc_limit = mcmc_limit_pool[2]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'NB'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_NB, extra_mcmc_NB = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_NB,extra_mcmc_NB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[4] == 1:
            # mcmc-GS #
            mcmc_limit = mcmc_limit_pool[4]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_GS, extra_mcmc_GS = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_GS,extra_mcmc_GS,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[8] == 1:
            # MKFS - W #
            mcmc_limit = mcmc_limit_pool[8]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsw'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'W'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSB, extra_mcmc_KFSB = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSB,extra_mcmc_KFSB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[6] == 1:
            # MKFS - P #
            mcmc_limit = mcmc_limit_pool[6]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsp'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'P'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSA, extra_mcmc_KFSA = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSA,extra_mcmc_KFSA,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        print('Success -- Iteration: '+ str(i+1) + '/' + str(iter_time) +  ' -- Time Elapsed:' + str(time.time()-start_time) + ' s')

    print('[@]End. Writing output file...')

    ## Output ##

    output_file_name = 'output/o_' + str(int(time.time())) + '_'

    # 1 - NB
    method = 'NB'
    func_Write_output(method,result_mcmc_NB,extra_mcmc_NB)
    # 2 - GS
    method = 'GS'
    func_Write_output(method,result_mcmc_GS,extra_mcmc_GS)
    # 3 - MKFSW
    method = 'KFSB'
    func_Write_output(method,result_mcmc_KFSB,extra_mcmc_KFSB)
    # 4 - MKFSP
    method = 'KFSA'
    func_Write_output(method,result_mcmc_KFSA,extra_mcmc_KFSA)

    # write parameter info #
    func_Write_info('Stage 4 Noise ' + str(noise_corr_time_rob[1]))

    print('[@]Output file written. S4 - Noise time ' + str(noise_corr_time_rob[1]))


    ## Iteration - 2 ##

    cal_type = ['I','R']
    noise_corr_time = noise_corr_time_rob[2]
    
    result_mcmc_NB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_GS = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSA = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]

    extra_mcmc_NB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_GS = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSA = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]

    print('[@][RUN -- LIKELIHOOD -- powell]')
    print('[@]Start. Total Iteration: ' + str(iter_time))

    func_Edit_cin()

    #start_time = time.time()

    for i in range(iter_time):

        ## Step 1 - Data Generation ##
        
        f = open(S1_cin_name,'r')
        lines = f.readlines()
        f.close()
        
        for j in range(len(lines)):
            if 'seed' in lines[j]:
                lines[j] = 'random seed = ' + str((i+1)*100) +' \n'
            if 'Noise correlation time' in lines[j]:
                lines[j] = 'Noise correlation time = ' + str(noise_corr_time) +' \n'
            if 'Noise Amp ED' in lines[j]:
                lines[j] = 'Noise Amp ED = ' + str(noise_2) +' \n'
            if 'Noise Amp ID' in lines[j]:
                lines[j] = 'Noise Amp ID = ' + str(noise_2) +' \n'
            if 'Noise Amp RD' in lines[j]:
                lines[j] = 'Noise Amp RD = ' + str(noise_2) +' \n'
            if 'Noise Amp ER' in lines[j]:
                lines[j] = 'Noise Amp ER = ' + str(noise_2) +' \n'
            if 'Noise Amp IR' in lines[j]:
                lines[j] = 'Noise Amp IR = ' + str(noise_2) +' \n'
            if 'Noise Amp RR' in lines[j]:
                lines[j] = 'Noise Amp RR = ' + str(noise_2) +' \n'
        f = open(S1_cin_name,'w')
        f.writelines(lines)
        f.close()
        
        temp_output_name = 'data.vdfx'
        if os.path.exists(temp_output_name):
            os.remove(temp_output_name)
        script_path = script_path_0 + cmd_file_name_d
        cmd = vensim_path + " \"" + script_path + "\""
        func_Run_command(cmd, max_repeat,temp_output_name)
        time.sleep(1)

        ## Step 2 - Estimation ##
        
        if scheme_flag[2] == 1:
            # mcmc-NB #
            mcmc_limit = mcmc_limit_pool[2]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'NB'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_NB, extra_mcmc_NB = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_NB,extra_mcmc_NB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[4] == 1:
            # mcmc-GS #
            mcmc_limit = mcmc_limit_pool[4]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_GS, extra_mcmc_GS = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_GS,extra_mcmc_GS,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[8] == 1:
            # MKFS - W #
            mcmc_limit = mcmc_limit_pool[8]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsw'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'W'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSB, extra_mcmc_KFSB = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSB,extra_mcmc_KFSB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[6] == 1:
            # MKFS - P #
            mcmc_limit = mcmc_limit_pool[6]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsp'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'P'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSA, extra_mcmc_KFSA = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSA,extra_mcmc_KFSA,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        print('Success -- Iteration: '+ str(i+1) + '/' + str(iter_time) +  ' -- Time Elapsed:' + str(time.time()-start_time) + ' s')

    print('[@]End. Writing output file...')

    ## Output ##

    output_file_name = 'output/o_' + str(int(time.time())) + '_'

    # 1 - NB
    method = 'NB'
    func_Write_output(method,result_mcmc_NB,extra_mcmc_NB)
    # 2 - GS
    method = 'GS'
    func_Write_output(method,result_mcmc_GS,extra_mcmc_GS)
    # 3 - MKFSW
    method = 'KFSB'
    func_Write_output(method,result_mcmc_KFSB,extra_mcmc_KFSB)
    # 4 - MKFSP
    method = 'KFSA'
    func_Write_output(method,result_mcmc_KFSA,extra_mcmc_KFSA)

    # write parameter info #
    func_Write_info('Stage 4 Noise ' + str(noise_corr_time_rob[2]))

    print('[@]Output file written. S4 - Noise time ' + str(noise_corr_time_rob[2]))

if run_s4_whitenoise_flag == 1:

    ## Iteration - WN ##

    cmd_file_name_d = cmd_file_name_WN    

    cal_type = ['I','R']
    noise_corr_time = noise_corr_time_rob[0]
    min_variance_F = min_variance_F_2
    
    result_mcmc_NB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_GS = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSB = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]
    result_mcmc_KFSA = [[[123456] for col in range(num_para+2)] for row in range(iter_time)]

    extra_mcmc_NB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_GS = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSB = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]
    extra_mcmc_KFSA = [[[123456] for col in range(num_para*statistics_item)] for row in range(iter_time)]

    print('[@][RUN -- LIKELIHOOD -- powell]')
    print('[@]Start. Total Iteration: ' + str(iter_time))

    func_Edit_cin()

    #start_time = time.time()

    for i in range(iter_time):

        ## Step 1 - Data Generation ##
        
        f = open(S1_cin_name,'r')
        lines = f.readlines()
        f.close()
        
        for j in range(len(lines)):
            if 'seed' in lines[j]:
                lines[j] = 'random seed = ' + str((i+1)*100) +' \n'
            if 'Noise correlation time' in lines[j]:
                lines[j] = 'Noise correlation time = ' + str(noise_corr_time) +' \n'
            if 'Noise Amp ED' in lines[j]:
                lines[j] = 'Noise Amp ED = ' + str(noise_2) +' \n'
            if 'Noise Amp ID' in lines[j]:
                lines[j] = 'Noise Amp ID = ' + str(noise_2) +' \n'
            if 'Noise Amp RD' in lines[j]:
                lines[j] = 'Noise Amp RD = ' + str(noise_2) +' \n'
            if 'Noise Amp ER' in lines[j]:
                lines[j] = 'Noise Amp ER = ' + str(noise_2) +' \n'
            if 'Noise Amp IR' in lines[j]:
                lines[j] = 'Noise Amp IR = ' + str(noise_2) +' \n'
            if 'Noise Amp RR' in lines[j]:
                lines[j] = 'Noise Amp RR = ' + str(noise_2) +' \n'
        f = open(S1_cin_name,'w')
        f.writelines(lines)
        f.close()
        
        temp_output_name = 'data.vdfx'
        if os.path.exists(temp_output_name):
            os.remove(temp_output_name)
        script_path = script_path_0 + cmd_file_name_d
        cmd = vensim_path + " \"" + script_path + "\""
        func_Run_command(cmd, max_repeat,temp_output_name)
        time.sleep(1)

        ## Step 2 - Estimation ##
        
        if scheme_flag[2] == 1:
            # mcmc-NB #
            mcmc_limit = mcmc_limit_pool[2]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'NB'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_NB, extra_mcmc_NB = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_NB,extra_mcmc_NB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[4] == 1:
            # mcmc-GS #
            mcmc_limit = mcmc_limit_pool[4]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N' 
            var_scaling = 'Y'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_GS, extra_mcmc_GS = func_Estimation(method,cmd_file_name3,method + '.out',result_mcmc_GS,extra_mcmc_GS,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[8] == 1:
            # MKFS - W #
            mcmc_limit = mcmc_limit_pool[8]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsw'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'W'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSB, extra_mcmc_KFSB = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSB,extra_mcmc_KFSB,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        if scheme_flag[6] == 1:
            # MKFS - P #
            mcmc_limit = mcmc_limit_pool[6]               
            mcmc_burnin = mcmc_limit - 1000
            method = 'mcmc_kfsp'
            SG_switch = 0
            restart_max = 10
            vpd_type = 'G'
            trans = 'N'
            var_scaling = 'Y'
            kf_opt = 'P'
            func_Edit_voc(method,restart_max,mcmc_limit,mcmc_burnin,max_iter)
            func_Edit_vpd(method,cal_type)
            result_mcmc_KFSA, extra_mcmc_KFSA = func_Estimation(method,cmd_file_name5,method + '.out',result_mcmc_KFSA,extra_mcmc_KFSA,i,SG_switch)
            print('Estimation Finished: ' + method)
            time.sleep(timeout_trial)
        
        print('Success -- Iteration: '+ str(i+1) + '/' + str(iter_time) +  ' -- Time Elapsed:' + str(time.time()-start_time) + ' s')

    print('[@]End. Writing output file...')

    ## Output ##

    output_file_name = 'output/o_' + str(int(time.time())) + '_'

    # 1 - NB
    method = 'NB'
    func_Write_output(method,result_mcmc_NB,extra_mcmc_NB)
    # 2 - GS
    method = 'GS'
    func_Write_output(method,result_mcmc_GS,extra_mcmc_GS)
    # 3 - MKFSW
    method = 'KFSB'
    func_Write_output(method,result_mcmc_KFSB,extra_mcmc_KFSB)
    # 4 - MKFSP
    method = 'KFSA'
    func_Write_output(method,result_mcmc_KFSA,extra_mcmc_KFSA)

    # write parameter info #
    func_Write_info('Stage 4 White Noise')

    print('[@]Output file written. S4 - White noise')