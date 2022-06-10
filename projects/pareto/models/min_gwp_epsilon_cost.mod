##########################
###   ADD PARAMETERS   ###
##########################
param TOTAL_COST_OP;
param EPSILON;

##########################
###   ADD CONSTRAINT   ###
##########################

# Epsilon space definition
subject to epsilon_space :
	TotalCost <= TOTAL_COST_OP * (1 + EPSILON);

##########################
### OBJECTIVE FUNCTION ###
##########################

# Minimize GWP on epsilon optimal space
minimize obj :
	TotalGWP;