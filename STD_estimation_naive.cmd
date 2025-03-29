! Estimation
SPECIAL>NOINTERACTION
SPECIAL>LOADMODEL|STD_SEIR_estimation.mdl

! Naive Powell
! Estimate should find the right optimum
! Important: Make sure the number after 'KALMAN' is 0
SIMULATE>RUNNAME|naive-GS.vdfx
SIMULATE>READCIN|SEIR_est.cin
SIMULATE>DATA|data.vdfx
SIMULATE>PAYOFF|payoff_naive.vpd
SIMULATE>OPTPARM|opt_naive.voc
SIMULATE>KALMAN|0
MENU>RUN_OPTIMIZE|o
!SPECIAL>CLEARRUNS
MENU>EXIT


