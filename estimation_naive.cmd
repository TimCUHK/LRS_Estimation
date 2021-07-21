! Estimation
SPECIAL>NOINTERACTION
SPECIAL>LOADMODEL|SEIR_estimation.mdl

! Naive Powell
! Estimate should find the right optimum
! Important: Make sure the number after 'KALMAN' is 0
SIMULATE>RUNNAME|naive-GS.vdf
SIMULATE>READCIN|SEIR_est.cin
SIMULATE>DATA|data.vdf
SIMULATE>PAYOFF|payoff_naive.vpd
SIMULATE>OPTPARM|opt_naive.voc
SIMULATE>KALMAN|0
MENU>RUN_OPTIMIZE|o
!SPECIAL>CLEARRUNS
MENU>EXIT


