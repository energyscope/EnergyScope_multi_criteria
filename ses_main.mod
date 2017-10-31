######################################################
#
# Swiss-EnergyScope (SES) MILP modeling framework
# Model file
# Author: Stefano Moret
# Date: 27.10.2017
# Model documentation: Moret S. (2017). "Strategic Energy Planning under Uncertainty". PhD Thesis n. 7961, EPFL, Switzerland (Chapter 1). (http://dx.doi.org/10.5075/epfl-thesis-7961)
# For terms of use and how to cite this work please check the ReadMe file. 
#
######################################################

### SETS [Figure 1.3] ###

## MAIN SETS: Sets whose elements are input directly in the data file
set PERIODS; # time periods
set SECTORS; # sectors of the energy system
set END_USES_INPUT; # Types of demand (end-uses). Input to the model
set END_USES_CATEGORIES; # Categories of demand (end-uses): electricity, heat, mobility
set END_USES_TYPES_OF_CATEGORY {END_USES_CATEGORIES}; # Types of demand (end-uses).
set RESOURCES; # Resources: fuels (wood and fossils) and electricity imports 
set BIOFUELS within RESOURCES; # imported biofuels.
set EXPORT within RESOURCES; # exported resources
set END_USES_TYPES := setof {i in END_USES_CATEGORIES, j in END_USES_TYPES_OF_CATEGORY [i]} j; # secondary set
set TECHNOLOGIES_OF_END_USES_TYPE {END_USES_TYPES}; # set all energy conversion technologies (excluding storage technologies)
set STORAGE_TECH; # set of storage technologies 
set INFRASTRUCTURE; # Infrastructure: DHN, grid, and intermediate energy conversion technologies (i.e. not directly supplying end-use demand)

## SECONDARY SETS: a secondary set is defined by operations on MAIN SETS
set LAYERS := (RESOURCES diff BIOFUELS diff EXPORT) union END_USES_TYPES; # Layers are used to balance resources/products in the system
set TECHNOLOGIES := (setof {i in END_USES_TYPES, j in TECHNOLOGIES_OF_END_USES_TYPE [i]} j) union STORAGE_TECH union INFRASTRUCTURE; 
set TECHNOLOGIES_OF_END_USES_CATEGORY {i in END_USES_CATEGORIES} within TECHNOLOGIES := setof {j in END_USES_TYPES_OF_CATEGORY[i], k in TECHNOLOGIES_OF_END_USES_TYPE [j]} k; 

## Additional SETS: only needed for printing out results
set COGEN within TECHNOLOGIES; # cogeneration tech
set BOILERS within TECHNOLOGIES; # boiler tech


### PARAMETERS [Table 1.1] ###
param end_uses_demand_year {END_USES_INPUT, SECTORS} >= 0 default 0; # end_uses_year: table end-uses demand vs sectors (input to the model). Yearly values.
param end_uses_input {i in END_USES_INPUT} := sum {s in SECTORS} (end_uses_demand_year [i,s]); # Figure 1.4: total demand for each type of end-uses across sectors (yearly energy) as input from the demand-side model
param i_rate > 0; # discount rate (real discount rate)

# Share public vs private mobility
param share_mobility_public_min >= 0, <= 1; # % min limit for penetration of public mobility over total mobility 
param share_mobility_public_max >= 0, <= 1; # % max limit for penetration of public mobility over total mobility 

# Share train vs truck in freight transportation
param share_freight_train_min >= 0, <= 1; # % min limit for penetration of train in freight transportation
param share_freight_train_max >= 0, <= 1; # % max limit for penetration of train in freight transportation

# Share dhn vs decentralized for low-T heating
param share_heat_dhn_min >= 0, <= 1; # % min limit for penetration of dhn in low-T heating
param share_heat_dhn_max >= 0, <= 1; # % max limit for penetration of dhn in low-T heating

param t_op {PERIODS}; # duration of each time period [h]
param lighting_month {PERIODS} >= 0, <= 1; # %_lighting: factor for sharing lighting across months (adding up to 1)
param heating_month {PERIODS} >= 0, <= 1; # %_sh: factor for sharing space heating across months (adding up to 1)

# f: input/output Resources/Technologies to Layers. Reference is one unit ([GW] or [Mpkm/h] or [Mtkm/h]) of (main) output of the resource/technology. input to layer (output of technology) > 0.
param layers_in_out {RESOURCES union TECHNOLOGIES diff STORAGE_TECH, LAYERS}; 

# Attributes of TECHNOLOGIES
param ref_size {TECHNOLOGIES} >= 0; # f_ref: reference size of each technology, expressed in the same units as the layers_in_out table. Refers to main output (heat for cogen technologies). storage level [GWh] for STORAGE_TECH
param c_inv {TECHNOLOGIES} >= 0; # Specific investment cost [MCHF/GW].[MCHF/GWh] for STORAGE_TECH
param c_maint {TECHNOLOGIES} >= 0; # O&M cost [MCHF/GW/year]: O&M cost does not include resource (fuel) cost. [MCHF/GWh] for STORAGE_TECH
param lifetime {TECHNOLOGIES} >= 0; # n: lifetime [years]
param f_max {TECHNOLOGIES} >= 0; # Maximum feasible installed capacity [GW], refers to main output. storage level [GWh] for STORAGE_TECH
param f_min {TECHNOLOGIES} >= 0; # Minimum feasible installed capacity [GW], refers to main output. storage level [GWh] for STORAGE_TECH
param fmax_perc {TECHNOLOGIES} >= 0, <= 1 default 1; # value in [0,1]: this is to fix that a technology can at max produce a certain % of the total output of its sector over the entire year
param fmin_perc {TECHNOLOGIES} >= 0, <= 1 default 0; # value in [0,1]: this is to fix that a technology can at min produce a certain % of the total output of its sector over the entire year
param c_p_t {TECHNOLOGIES, PERIODS} >= 0, <= 1 default 1; # capacity factor of each technology and resource, defined on monthly basis. Different than 1 if F_Mult_t (t) <= c_p_t (t) * F_Mult
param c_p {TECHNOLOGIES} >= 0, <= 1 default 1; # capacity factor of each technology, defined on annual basis. Different than 1 if sum {t in PERIODS} F_Mult_t (t) * t_op (t) <= c_p * F_Mult
param tau {i in TECHNOLOGIES} := i_rate * (1 + i_rate)^lifetime [i] / (((1 + i_rate)^lifetime [i]) - 1); # Annualisation factor for each different technology
param gwp_constr {TECHNOLOGIES} >= 0; # GWP emissions associated to the construction of technologies [ktCO2-eq./GW]. Refers to [GW] of main output
param total_time := sum {t in PERIODS} (t_op [t]); # added just to simplify equations

# Attributes of RESOURCES
param c_op {RESOURCES, PERIODS} >= 0; # cost of resources in the different periods [MCHF/GWh]
param avail {RESOURCES} >= 0; # Yearly availability of resources [GWh/y]
param gwp_op {RESOURCES} >= 0; # GWP emissions associated to the use of resources [ktCO2-eq./GWh]. Includes extraction/production/transportation and combustion

# Attributes of STORAGE_TECH
param storage_eff_in {STORAGE_TECH, LAYERS} >= 0, <= 1; # eta_sto_in: efficiency of input to storage from layers.  If 0 storage_tech/layer are incompatible
param storage_eff_out {STORAGE_TECH, LAYERS} >= 0, <= 1; # eta_sto_out: efficiency of output from storage to layers. If 0 storage_tech/layer are incompatible

# Losses in the networks
param loss_coeff {END_USES_TYPES} >= 0 default 0; # 0 in all cases apart from electricity grid and DHN
param peak_dhn_factor >= 0;


## VARIABLES [Tables 1.2, 1.3] ###
var End_Uses {LAYERS, PERIODS} >= 0; # total demand for each type of end-uses (monthly power). Defined for all layers (0 if not demand)
var Number_Of_Units {TECHNOLOGIES} integer; # N: number of units of size ref_size which are installed.
var F_Mult {TECHNOLOGIES} >= 0; # F: installed size, multiplication factor with respect to the values in layers_in_out table
var F_Mult_t {RESOURCES union TECHNOLOGIES, PERIODS} >= 0; # F_t: Operation in each period. multiplication factor with respect to the values in layers_in_out table. Takes into account c_p
var C_inv {TECHNOLOGIES} >= 0; # Total investment cost of each technology
var C_maint {TECHNOLOGIES} >= 0; # Total O&M cost of each technology (excluding resource cost)
var C_op {RESOURCES} >= 0; # Total O&M cost of each resource
var Storage_In {i in STORAGE_TECH, LAYERS, PERIODS} >= 0; # Sto_in: Power [GW] input to the storage in a certain period
var Storage_Out {i in STORAGE_TECH, LAYERS, PERIODS} >= 0; # Sto_out: Power [GW] output from the storage in a certain period
var Share_Mobility_Public >= share_mobility_public_min, <= share_mobility_public_max; # %_Public: % of passenger mobility attributed to public transportation
var Share_Freight_Train, >= share_freight_train_min, <= share_freight_train_max; # %_Rail: % of freight mobility attributed to train
var Share_Heat_Dhn, >= share_heat_dhn_min, <= share_heat_dhn_max; # %_Dhn: % of low-T heat demand attributed to DHN
var Y_Solar_Backup {TECHNOLOGIES} binary; # Y_Solar: binary variable. if 1, identifies the decentralized technology (only 1) which is backup for solar. 0 for all other technologies
var Losses {END_USES_TYPES, PERIODS} >= 0; # Loss: Losses in the networks (normally electricity grid and DHN)
var GWP_constr {TECHNOLOGIES} >= 0; # Total emissions of the technologies [ktCO2-eq.]
var GWP_op {RESOURCES} >= 0; # Total yearly emissions of the resources [ktCO2-eq./y]
var TotalGWP >= 0; # GWP_tot: Total global warming potential (GWP) emissions in the system [ktCO2-eq./y]
var TotalCost >= 0; # C_tot: Total GWP emissions in the system [ktCO2-eq./y]


### CONSTRAINTS ###

## End-uses demand calculation constraints 

# [Figure 1.4] From annual energy demand to monthly power demand. End_Uses is non-zero only for demand layers.
subject to end_uses_t {l in LAYERS, t in PERIODS}:
	End_Uses [l,t] = (if l == "ELECTRICITY" 
		then
			(end_uses_input[l] / total_time + end_uses_input["LIGHTING"] * lighting_month [t] / t_op [t]) + Losses [l,t]
		else (if l == "HEAT_LOW_T_DHN" then
			(end_uses_input["HEAT_LOW_T_HW"] / total_time + end_uses_input["HEAT_LOW_T_SH"] * heating_month [t] / t_op [t]) * Share_Heat_Dhn + Losses [l,t]
		else (if l == "HEAT_LOW_T_DECEN" then
			(end_uses_input["HEAT_LOW_T_HW"] / total_time + end_uses_input["HEAT_LOW_T_SH"] * heating_month [t] / t_op [t]) * (1 - Share_Heat_Dhn)
		else (if l == "MOB_PUBLIC" then
			(end_uses_input["MOBILITY_PASSENGER"] / total_time) * Share_Mobility_Public
		else (if l == "MOB_PRIVATE" then
			(end_uses_input["MOBILITY_PASSENGER"] / total_time) * (1 - Share_Mobility_Public)
		else (if l == "MOB_FREIGHT_RAIL" then
			(end_uses_input["MOBILITY_FREIGHT"] / total_time) * Share_Freight_Train
		else (if l == "MOB_FREIGHT_ROAD" then
			(end_uses_input["MOBILITY_FREIGHT"] / total_time) * (1 - Share_Freight_Train)
		else (if l == "HEAT_HIGH_T" then
			end_uses_input[l] / total_time
		else 
			0 )))))))); # For all layers which don't have an end-use demand
	
## Multiplication factor

# [Eq. 1.7] Number of purchased technologies. Integer variable (so that we have only integer multiples of the reference size)
subject to number_of_units {i in TECHNOLOGIES diff INFRASTRUCTURE}:
	Number_Of_Units [i] = F_Mult [i] / ref_size [i]; 
	
# [Eq. 1.6] min & max limit to the size of each technology
subject to size_limit {i in TECHNOLOGIES}:
	f_min [i] <= F_Mult [i] <= f_max [i];
	
# [Eq. 1.8] relation between mult_t and mult via period capacity factor. This forces max monthly output (e.g. renewables)
subject to capacity_factor_t {i in TECHNOLOGIES, t in PERIODS}:
	F_Mult_t [i, t] <= F_Mult [i] * c_p_t [i, t];
	
# [Eq. 1.9] relation between mult_t and mult via yearly capacity factor. This one forces total annual output
subject to capacity_factor {i in TECHNOLOGIES}:
	sum {t in PERIODS} (F_Mult_t [i, t] * t_op [t]) <= F_Mult [i] * c_p [i] * total_time;	
	
# [Eq. 1.19] Operating strategy in the for decentralized heat supply: output heat in each month proportional to installed capacity (more realistic).
# When solar thermal is installed, it replaces one technology which is chosen as backup. The sum of the % production of solar + backup must respect the minimum share of the backup technology
# Here written in a compact non linear form, below it is linearized  
# subject to op_strategy_decen_1 {i in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, t in PERIODS}:
#	  F_Mult_t [i, t] + F_Mult_t ["DEC_SOLAR", t] * y_solar_backup [i] >= sum {t2 in PERIODS} (F_Mult_t [i, t2] * t_op [t2]) * ((end_uses_input["HEAT_LOW_T_HW"] / total_time + end_uses_input["HEAT_LOW_T_SH"] * heating_month [t] / t_op [t]) / (end_uses_input["HEAT_LOW_T_HW"] + end_uses_input["HEAT_LOW_T_SH"]));

# Linearization of Eq. 1.19
# Auxiliary variable 
var X_Solar_Backup_Aux {TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, t in PERIODS} >= 0;

subject to op_strategy_decen_1_linear {i in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, t in PERIODS}:
	F_Mult_t [i, t] + X_Solar_Backup_Aux [i, t] >= sum {t2 in PERIODS} (F_Mult_t [i, t2] * t_op [t2]) * ((end_uses_input["HEAT_LOW_T_HW"] / total_time + end_uses_input["HEAT_LOW_T_SH"] * heating_month [t] / t_op [t]) / (end_uses_input["HEAT_LOW_T_HW"] + end_uses_input["HEAT_LOW_T_SH"]));

# These three constraints impose that: X_solar_backup_aux [i, t] = F_Mult_t ["DEC_SOLAR", t] * y_solar_backup [i]
# from: http://www.leandro-coelho.com/linearization-product-variables/
subject to op_strategy_decen_1_linear_1 {i in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, t in PERIODS}:
	X_Solar_Backup_Aux [i, t] <= f_max ["DEC_SOLAR"] * Y_Solar_Backup [i];

subject to op_strategy_decen_1_linear_2 {i in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, t in PERIODS}:
	X_Solar_Backup_Aux [i, t] <= F_Mult_t ["DEC_SOLAR", t];

subject to op_strategy_decen_1_linear_3 {i in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, t in PERIODS}:
	X_Solar_Backup_Aux [i, t] >= F_Mult_t ["DEC_SOLAR", t] - (1 - Y_Solar_Backup [i]) * f_max ["DEC_SOLAR"];

# [Eq. 1.20] Only one technology can be backup of solar
subject to op_strategy_decen_2:
	sum {i in TECHNOLOGIES} Y_Solar_Backup [i] <= 1;

## Layers

# [Eq. 1.13] Layer balance equation with storage. Layers: input > 0, output < 0. Demand > 0. Storage: in > 0, out > 0;
# output from technologies/resources/storage - input to technologies/storage = demand. Demand has default value of 0 for layers which are not end_uses
subject to layer_balance {l in LAYERS, t in PERIODS}:
	0 = 
		sum {i in RESOURCES union TECHNOLOGIES diff STORAGE_TECH} (layers_in_out[i, l] * F_Mult_t [i, t]) 
		+ sum {j in STORAGE_TECH} (Storage_Out [j, l, t] - Storage_In [j, l, t])
		- End_Uses [l, t];

## Resources

# [Eq. 1.12] Resources availability equation
subject to resource_availability {i in RESOURCES}:
	sum {t in PERIODS} (F_Mult_t [i, t] * t_op [t]) <= avail [i];

## Storage

# [Eq. 1.15-1.16] Each storage technology can have input/output only to certain layers. If incompatible then the variable is set to 0
# ceil (x) operator rounds a number to the highest nearest integer. 
subject to storage_layer_in {i in STORAGE_TECH, l in LAYERS, t in PERIODS}:
	Storage_In [i, l, t] * (ceil (storage_eff_in [i, l]) - 1) = 0;

subject to storage_layer_out {i in STORAGE_TECH, l in LAYERS, t in PERIODS}:
	Storage_Out [i, l, t] * (ceil (storage_eff_out [i, l]) - 1) = 0;

# [Eq. 1.14] Storage can't be a transfer unit in a given period: either output or input.
# Nonlinear formulation would be as follows:
# subject to storage_no_transfer {i in STORAGE_TECH, t in PERIODS}:
# 	ceil (sum {l in LAYERS: storage_eff_in [i,l] > 0} (Storage_In [i, l, t] * storage_eff_in_mult [i, l])  * t_op [t] / f_max [i]) +
# 	ceil (sum {l in LAYERS: storage_eff_out [i,l] > 0} (Storage_Out [i, l, t] / storage_eff_out_mult [i, l])  * t_op [t] / f_max [i]) <= 1;
# Could be written in a linear way as follows (3 equations):

# Linearization of Eq. 1.14
var Y_Sto_In {STORAGE_TECH, PERIODS} binary;
var Y_Sto_Out {STORAGE_TECH, PERIODS} binary;

subject to storage_no_transfer_1 {i in STORAGE_TECH, t in PERIODS}:
	(sum {l in LAYERS: storage_eff_in [i,l] > 0} (Storage_In [i, l, t] * storage_eff_in [i, l])) * t_op [t] / f_max [i] <= Y_Sto_In [i, t];
	
subject to storage_no_transfer_2 {i in STORAGE_TECH, t in PERIODS}:
	(sum {l in LAYERS: storage_eff_out [i,l] > 0} (Storage_Out [i, l, t] / storage_eff_out [i, l])) * t_op [t] / f_max [i] <= Y_Sto_Out [i, t];

subject to storage_no_transfer_3 {i in STORAGE_TECH, t in PERIODS}:
	Y_Sto_In [i,t] + Y_Sto_Out [i,t] <= 1;

# [Eq. 1.14] The level of the storage represents the amount of energy stored at a certain time.
subject to storage_level {i in STORAGE_TECH, t in PERIODS}:
	F_Mult_t [i, t] = (if t == 1 then
	 			F_Mult_t [i, card(PERIODS)] + ((sum {l in LAYERS: storage_eff_in [i,l] > 0} (Storage_In [i, l, t] * storage_eff_in [i, l])) 
					- (sum {l in LAYERS: storage_eff_out [i,l] > 0} (Storage_Out [i, l, t] / storage_eff_out [i, l]))) * t_op [t]
	else
	 			F_Mult_t [i, t-1] + ((sum {l in LAYERS: storage_eff_in [i,l] > 0} (Storage_In [i, l, t] * storage_eff_in [i, l])) 
					- (sum {l in LAYERS: storage_eff_out [i,l] > 0} (Storage_Out [i, l, t] / storage_eff_out [i, l]))) * t_op [t]);
								
## [Eq. 1.18] Calculation of losses for each end-use demand type (normally for electricity and DHN)
subject to network_losses {i in END_USES_TYPES, t in PERIODS}:
	Losses [i,t] = (sum {j in RESOURCES union TECHNOLOGIES diff STORAGE_TECH: layers_in_out [j, i] > 0} ((layers_in_out[j, i]) * F_Mult_t [j, t])) * loss_coeff [i];

## Additional constraints: Constraints needed for the application to Switzerland (not needed in standard MILP formulation)

# [Eq 1.22] Definition of min/max output of each technology as % of total output in a given layer. 
# Normally for a tech should use either f_max/f_min or f_max_%/f_min_%
subject to f_max_perc {i in END_USES_TYPES, j in TECHNOLOGIES_OF_END_USES_TYPE[i]}:
	sum {t in PERIODS} (F_Mult_t [j, t] * t_op[t]) <= fmax_perc [j] * sum {j2 in TECHNOLOGIES_OF_END_USES_TYPE[i], t2 in PERIODS} (F_Mult_t [j2, t2] * t_op [t2]);

subject to f_min_perc {i in END_USES_TYPES, j in TECHNOLOGIES_OF_END_USES_TYPE[i]}:
	sum {t in PERIODS} (F_Mult_t [j, t] * t_op[t])  >= fmin_perc [j] * sum {j2 in TECHNOLOGIES_OF_END_USES_TYPE[i], t2 in PERIODS} (F_Mult_t [j2, t2] * t_op [t2]);

## [Eq. 1.24] Seasonal storage in hydro dams.
# When installed power of new dams 0 -> 0.44, maximum storage capacity changes linearly 0 -> 2400 GWh/y
subject to storage_level_hydro_dams: 
	F_Mult ["PUMPED_HYDRO"] <= f_max ["PUMPED_HYDRO"] * (F_Mult ["NEW_HYDRO_DAM"] - f_min ["NEW_HYDRO_DAM"])/(f_max ["NEW_HYDRO_DAM"] - f_min ["NEW_HYDRO_DAM"]);

# [Eq. 1.25] Hydro dams can only shift production. Efficiency is 1, "storage" is actually only avoided production shifted to different months
subject to hydro_dams_shift {t in PERIODS}: 
	Storage_In ["PUMPED_HYDRO", "ELECTRICITY", t] <= (F_Mult_t ["HYDRO_DAM", t] + F_Mult_t ["NEW_HYDRO_DAM", t]);

## [Eq. 1.26] DHN: assigning a cost to the network	
subject to extra_dhn:
	F_Mult ["DHN"] = sum {j in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DHN"]} (F_Mult [j]);

# [Eq. 1.27] Calculation of max heat demand in DHN 
var Max_Heat_Demand_DHN >= 0;

subject to max_dhn_heat_demand {t in PERIODS}:
	Max_Heat_Demand_DHN >= End_Uses ["HEAT_LOW_T_DHN", t];

# Peak in DHN
subject to peak_dhn:
	sum {j in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DHN"]} (F_Mult [j]) >= peak_dhn_factor * Max_Heat_Demand_DHN;

# [Eq. 1.28] 9.4 BCHF is the extra investment needed if there is a big deployment of stochastic renewables
subject to extra_grid:
	F_Mult ["GRID"] = 1 + (9400 / c_inv["GRID"]) * (F_Mult ["WIND"] + F_Mult ["PV"]) / (f_max ["WIND"] + f_max ["PV"]);

# [Eq. 1.29] Power2Gas investment cost is calculated on the max size of the two units
subject to extra_power2gas_1:
	F_Mult ["POWER2GAS_3"] >= F_Mult ["POWER2GAS_1"];
	
subject to extra_power2gas_2:
	F_Mult ["POWER2GAS_3"] >= F_Mult ["POWER2GAS_2"];

# [Eq. 1.23] Operating strategy in private mobility (to make model more realistic)
# Mobility share is fixed as constant in the different months. This constraint is needed only if c_inv = 0 for mobility.
subject to op_strategy_mob_private {i in TECHNOLOGIES_OF_END_USES_CATEGORY["MOBILITY_PASSENGER"] union TECHNOLOGIES_OF_END_USES_CATEGORY["MOBILITY_FREIGHT"], t in PERIODS}:
	F_Mult_t [i, t]  >= sum {t2 in PERIODS} (F_Mult_t [i, t2] * t_op [t2] / total_time);
	
# Energy efficiency is a fixed cost
subject to extra_efficiency:
	F_Mult ["EFFICIENCY"] = 1 / (1 + i_rate);	

## Cost

# [Eq. 1.3] Investment cost of each technology
subject to investment_cost_calc {i in TECHNOLOGIES}: # add storage investment cost
	C_inv [i] = c_inv [i] * F_Mult [i];
		
# [Eq. 1.4] O&M cost of each technology
subject to main_cost_calc {i in TECHNOLOGIES}: # add storage investment
	C_maint [i] = c_maint [i] * F_Mult [i];		

# [Eq. 1.10] Total cost of each resource
subject to op_cost_calc {i in RESOURCES}:
	C_op [i] = sum {t in PERIODS} (c_op [i, t] * F_Mult_t [i, t] * t_op [t]);

# [Eq. 1.1]	
subject to totalcost_cal:
	TotalCost = sum {i in TECHNOLOGIES} (tau [i]  * C_inv [i] + C_maint [i]) + sum {j in RESOURCES} C_op [j];
	
## Emissions

# [Eq. 1.5]
subject to gwp_constr_calc {i in TECHNOLOGIES}:
	GWP_constr [i] = gwp_constr [i] * F_Mult [i];

# [Eq. 1.10]
subject to gwp_op_calc {i in RESOURCES}:
	GWP_op [i] = gwp_op [i] * sum {t in PERIODS} (t_op [t] * F_Mult_t [i, t]);	

# [Eq. 1.21]
subject to totalGWP_calc:
	TotalGWP = sum {i in TECHNOLOGIES} (GWP_constr [i] / lifetime [i]) + sum {j in RESOURCES} GWP_op [j];

### OBJECTIVE FUNCTION ###

# Can choose between TotalGWP and TotalCost
minimize obj: TotalCost; 
