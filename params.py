import time

iter_time = 100     
percentile_list = [[45,55],[40,60],[35,65],[30,70],[25,75],[20,80],[15,85],[10,90],[5,95]]
statistics_item = 7 + 2*len(percentile_list) # count,min,max,mean,median,std,norm_std, percentile 9*2
#name_para = ['contact rate','incubation period','infection period','Noise Amp D','Noise Amp R','r','Noise correlation time']   
name_para = ['contact rate','incubation period','infection period','Noise Amp D','Autocorrelated Noise STD','r','Noise correlation time']
num_para = 6
#range_para = [[1,3,50],[1,5,50],[1,5,50],[0,0.1,20],[0,0.1,20],[0.1,2,10],[1,5,20]]  # for non-standard SEIR
range_para = [[1,3,50],[1,8,50],[1,5,50],[0,0.1,20],[0,0.3,1],[0.1,2,10],[1,5,20]]  # for standard SEIR

restart_max = 10                # For "multiple_restart" at .voc file
#mcmc_limit = 12000               # For "MCLIMIT" at .voc file
#mcmc_burnin = 11000                # For "MCBURNIN" at .voc file
max_iter = 1000

cal_type = ['E','I','R']    # pool : ['E','I','R']

est_time_step = 0.125
min_variance_F = 2e6    # 1e3 for noise = 0.1; 5e4 for noise = 0.3; 2e6 for noise = 0.5 
min_variance_F_2 = 2e6  # 2e6 for noise = 0.5 
IV_for_SEIR = 1e6       # 1e6 works well
IV_for_Noise = 1e0      # 1e0 or 1e3 for noise = 0.1/0.3, 1e0 for noise = 0.5

noise_1 = 0.3
noise_2 = 0.5
noise_corr_time = 5
noise_corr_time_rob = [5,2,8]

vpd_type = 'G'
trans = 'N'
var_scaling = 'Y'
vpd_FS = 'F'         # 'F' (using flow) or 'S' (using stock) when matching the data
kf_opt = 'W'         # 'W' (white noise formulation) or 'P' (pink noise formulation) for KF

S1_cin_name = 'SEIR_dg.cin'
S2_cin_name = 'SEIR_est.cin'

vensim_path = 'C:/Program Files/Vensim/vendss64.exe'       # Edit for local usage ! #
script_path_0 = 'C:/Users/"Tianyi Li"/Desktop/2021LRS/LRS_Estimation_Code_check/'  # Edit for local usage ! #

timeout_trial = 3  
timeout_run = 500 
max_repeat = 5


STD_flag = 1

if STD_flag == 1:
    prefix = 'STD_'
if STD_flag == 0:
    prefix = ''
    
cmd_file_name_d  = prefix + 'data_generation.cmd'
cmd_file_name_WN = prefix + 'data_generation_WN.cmd'         # For white measurement noise: cmd_file_name_d = cmd_file_name_WN          
cmd_file_name_SG = prefix + 'data_generation_SG.cmd'
cmd_file_name1   = prefix + 'estimation_naive.cmd'
cmd_file_name2   = prefix + 'estimation_kf.cmd'
cmd_file_name3   = prefix + 'estimation_mcmc.cmd'
cmd_file_name4   = prefix + 'estimation_kf_mcmc.cmd'
cmd_file_name5   = prefix + 'estimation_mcmc_kf.cmd'
cmd_file_name6   = prefix + 'estimation_naive_mcmc.cmd'

output_file_name = 'output/o_' + str(int(time.time())) + '_'

run_s1_mcmc_flag = 0
run_s1_naive_flag = 0
run_s2_flag = 0
run_s3_1_flag = 0
run_s3_2_flag = 0
run_s4_flag = 0
run_s4_noisetime_flag = 1
run_s4_whitenoise_flag = 1

scheme_flag = [0,0,1,0,1,0,1,0,1]  #[G,P,NB,GL,GS,KFA,KFSA,KFB,KFSB]
mcmc_limit_pool = [10000,5000,7000,10000,10000,7000,10000,5000,5000]

#mcmc_limit_pool = [i + 1000 for i in mcmc_limit_pool]
#mcmc_limit_pool = [5000,5000,5000,5000,5000,5000,5000,5000,5000]
