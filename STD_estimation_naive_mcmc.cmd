! Estimation
SPECIAL>NOINTERACTION
SPECIAL>LOADMODEL|STD_SEIR_estimation.mdl

! Naive + MCMC
! Estimate should find the right optimum
! Important: Make sure the number after 'KALMAN' is 0

SIMULATE>RUNNAME|naive_mcmc-GS.vdf
SIMULATE>READCIN|SEIR_est.cin
SIMULATE>DATA|data.vdf
SIMULATE>PAYOFF|payoff_naive_mcmc.vpd
SIMULATE>OPTPARM|opt_naive_mcmc.voc
SIMULATE>KALMAN|0
MENU>RUN_OPTIMIZE|o


! export sample and all points
MENU>TAB2VDF|naive_mcmc_sample.tab||tab_MCMC.frm
!MENU>TAB2VDF|naive_mcmc_points.tab||tab_MCMC.frm
!SPECIAL>CLEARRUNS
MENU>EXIT


