##########################
###   ADD PARAMETERS   ###
##########################
param TOTAL_EINV_OP;
param EPSILON_EINV;

##########################
###   ADD CONSTRAINT   ###
##########################

# Epsilon space definition
subject to epsilon_space_einv :
	TotalEinv <= TOTAL_EINV_OP * (1 + EPSILON_EINV);

##########################
### OBJECTIVE FUNCTION ###
##########################

# Minimize Einv on epsilon optimal space
minimize obj :
	TotalCost;