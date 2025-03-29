! Estimation
SPECIAL>NOINTERACTION
SPECIAL>LOADMODEL|STD_SEIR_estimation.mdl

! MCMC
! Estimate should find the right optimum
! Important: Make sure the number after 'KALMAN' is 0

SIMULATE>RUNNAME|mcmc.vdfx
SIMULATE>READCIN|SEIR_est.cin
SIMULATE>DATA|data.vdfx
SIMULATE>PAYOFF|payoff_mcmc.vpd
SIMULATE>OPTPARM|opt_mcmc.voc
SIMULATE>KALMAN|0
MENU>RUN_OPTIMIZE|o

! export the MCMC stats for viewing
!MENU>DAT2VDF|mcmc_stats.dat
! export sample and all points
MENU>TAB2VDF|mcmc_sample.tab||tab_MCMC.frm
!MENU>TAB2VDF|mcmc_points.tab||tab_MCMC.frm
!SPECIAL>CLEARRUNS
MENU>EXIT


