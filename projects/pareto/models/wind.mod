##########################
###   ADD PARAMETERS   ###
##########################
param TOTAL_COST_OP;
param TOTAL_EINV_OP;
param EPSILON_COST;
param EPSILON_EINV;
set TECHNOLOGIES_TO_MINIMIZE;

##########################
###   ADD CONSTRAINT   ###
##########################

# Epsilon space definition
subject to epsilon_space_cost :
	TotalCost <= TOTAL_COST_OP * (1 + EPSILON_COST);

subject to epsilon_space_einv :
	TotalEinv <= TOTAL_EINV_OP * (1 + EPSILON_EINV);

##########################
### OBJECTIVE FUNCTION ###
##########################

# Minimize sum of capacities
minimize obj :
	sum {j in TECHNOLOGIES_TO_MINIMIZE} F[j] ;