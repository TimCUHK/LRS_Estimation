import time

iter_time = 100          
percentile_list = [[45,55],[40,60],[35,65],[30,70],[25,75],[20,80],[15,85],[10,90],[5,95]]
statistics_item = 7 + 2*len(percentile_list)
                                # count,min,max,mean,median,std,norm_std, percentile 9*2
name_para = ['contact rate','incubation period','infection period','Noise Amp D','Noise Amp R','r','Noise correlation time']   
num_para = 6                    # number of parameters in optimization
range_para = [[1,3,20],[1,5,20],[1,5,20],[0,0.1,20],[0,0.1,20],[0.1,2,10],[1,5,20]]

restart_max = 10                # For "multiple_restart" at .voc file
mcmc_limit = 4000               # For "MCLIMIT" at .voc file
mcmc_burnin = 3000              # For "MCBURNIN" at .voc file
max_iter = 1000

cal_type = ['I','R']            # pool : ['E','I','R']  --> data availability

est_time_step = 0.125
min_variance_F = 1e4
IV = 1e6

vpd_type = 'G'                  # 'G' (Gaussian), 'P' (Poisson), 'B' (Binomial), 'NB' (negative binomial)
trans = 'N'                     # 'Y' or 'N' for log transform
var_scaling = 'Y'               # 'Y' or 'N' for manual variance scaling
vpd_FS = 'F'                    # 'F' (using flow) or 'S' (using stock) when matching the data
kf_opt = 'W'                    # 'W' (white noise formulation) or 'P' (pink noise formulation) for KF

    
S1_cin_name = 'SEIR_dg.cin'
S2_cin_name = 'SEIR_est.cin'

vensim_path = 'C:/"Program Files (x86)"/Vensim/vensim.exe'           # Edit for local usage ! #
script_path_0 = 'C:/Users/EDZ/Desktop/LRS_Parameter_Estimation/'     # Edit for local usage ! #

timeout_trial = 3  
timeout_run = 10000 
max_repeat = 15

cmd_file_name_d = 'data_generation.cmd'
cmd_file_name1 = 'estimation_naive.cmd'
cmd_file_name2 = 'estimation_kf.cmd'
cmd_file_name3 = 'estimation_mcmc.cmd'
cmd_file_name4 = 'estimation_kf_mcmc.cmd'
cmd_file_name5 = 'estimation_mcmc_kf.cmd'
cmd_file_name6 = 'estimation_naive_mcmc.cmd'


output_file_name = 'output/o_' + str(int(time.time())) + '_'

