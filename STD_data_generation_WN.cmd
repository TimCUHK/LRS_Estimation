! Data generation
SPECIAL>NOINTERACTION
SPECIAL>LOADMODEL|STD_SEIR_data_generation_white_meas_noise.mdl

! ordinary simulation
SIMULATE>RUNNAME|data.vdfx
SIMULATE>READCIN|SEIR_dg.cin
MENU>RUN|o
MENU>VDF2CSV|!|!|
!SPECIAL>CLEARRUNS
MENU>EXIT
