##########################
###   ADD PARAMETERS   ###
##########################
param TOTAL_EINV_OP;
param EPSILON;

##########################
###   ADD CONSTRAINT   ###
##########################

# Epsilon space definition
subject to epsilon_space_einv :
	TotalEinv <= TOTAL_EINV_OP * (1 + EPSILON);

##########################
### OBJECTIVE FUNCTION ###
##########################

# Minimize Cost on epsilon optimal space
minimize obj :
	TotalCost;