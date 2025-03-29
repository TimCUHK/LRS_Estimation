! Estimation
SPECIAL>NOINTERACTION
SPECIAL>LOADMODEL|STD_SEIR_estimation.mdl

! Naive Powell + Kalman Filtering
! Estimate should find the right optimum
! Important: Make sure the number after 'KALMAN' is 1 
SIMULATE>RUNNAME|pkfs.vdf
SIMULATE>READCIN|SEIR_est.cin
SIMULATE>DATA|data.vdf
SIMULATE>PAYOFF|payoff_kf.vpd
SIMULATE>OPTPARM|opt_kf.voc
SIMULATE>KALMAN|1
MENU>RUN_OPTIMIZE|o
!SPECIAL>CLEARRUNS
MENU>EXIT


