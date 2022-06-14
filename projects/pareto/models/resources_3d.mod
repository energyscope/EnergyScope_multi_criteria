##########################
###   ADD PARAMETERS   ###
##########################
param TOTAL_COST_OP;
param TOTAL_EINV_OP;
param TOTAL_GWP_OP;
param EPSILON_COST;
param EPSILON_EINV;
param EPSILON_GWP;
set RESOURCES_TO_MINIMIZE;

##########################
###   ADD CONSTRAINT   ###
##########################

# Epsilon space definition
subject to epsilon_space_cost :
	TotalCost <= TOTAL_COST_OP * (1 + EPSILON_COST);

subject to epsilon_space_einv :
	TotalEinv <= TOTAL_EINV_OP * (1 + EPSILON_EINV);

subject to epsilon_space_gwp :
	TotalGWP <= TOTAL_GWP_OP * (1 + EPSILON_GWP);

##########################
### OBJECTIVE FUNCTION ###
##########################

# Minimize sum usage of resources
minimize obj :
	sum {j in RESOURCES_TO_MINIMIZE, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (F_t [j, h, td] * t_op [h, td]);