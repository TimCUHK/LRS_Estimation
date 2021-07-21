! Estimation
SPECIAL>NOINTERACTION
SPECIAL>LOADMODEL|SEIR_estimation_p.mdl

! MCMC
! Estimate should find the right optimum
! Important: Make sure the number after 'KALMAN' is 0

SIMULATE>RUNNAME|mcmc_kfsp.vdf
SIMULATE>READCIN|SEIR_est.cin
SIMULATE>DATA|data.vdf
SIMULATE>PAYOFF|payoff_mcmc_kf.vpd
SIMULATE>OPTPARM|opt_mcmc_kf.voc
SIMULATE>KALMAN|1
MENU>RUN_OPTIMIZE|o

! export the MCMC stats for viewing
!MENU>DAT2VDF|mcmc_kf_stats.dat
! export sample and all points
MENU>TAB2VDF|mcmc_kf_sample.tab||tab_MCMC.frm
!MENU>TAB2VDF|mcmc_kf_points.tab||tab_MCMC.frm
!SPECIAL>CLEARRUNS
MENU>EXIT


