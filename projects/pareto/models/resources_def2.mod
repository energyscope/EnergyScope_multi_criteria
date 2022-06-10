##########################
###   ADD PARAMETERS   ###
##########################
param EPSILON_COST;
param EPSILON_EINV;
param PARETO_SOLUTION_COST;
param PARETO_SOLUTION_EINV;
set RESOURCES_TO_MINIMIZE;

##########################
###   ADD CONSTRAINT   ###
##########################

# Epsilon space definition
subject to epsilon_space_cost :
	TotalCost <= PARETO_SOLUTION_COST * (1 + EPSILON_COST);

subject to epsilon_space_einv :
	TotalEinv <= PARETO_SOLUTION_EINV * (1 + EPSILON_EINV);

##########################
### OBJECTIVE FUNCTION ###
##########################

# Minimize sum usage of resources
minimize obj :
	sum {j in RESOURCES_TO_MINIMIZE, h in HOURS, td in TYPICAL_DAYS} F_t[j, h, td];