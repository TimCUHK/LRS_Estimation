! Estimation
SPECIAL>NOINTERACTION
SPECIAL>LOADMODEL|STD_SEIR_estimation.mdl

! KF + MCMC
! Estimate should find the right optimum
! Important: Make sure the number after 'KALMAN' is 1

SIMULATE>RUNNAME|kf_mcmc.vdf
SIMULATE>READCIN|SEIR_est.cin
SIMULATE>DATA|data.vdf
SIMULATE>PAYOFF|payoff_kf_mcmc.vpd
SIMULATE>OPTPARM|opt_kf_mcmc.voc
SIMULATE>KALMAN|1
MENU>RUN_OPTIMIZE|o


! export sample and all points
MENU>TAB2VDF|kf_mcmc_sample.tab||tab_MCMC.frm
!MENU>TAB2VDF|kf_mcmc_points.tab||tab_MCMC.frm
!SPECIAL>CLEARRUNS
MENU>EXIT


