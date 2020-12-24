# -------------------------------------------------------------------------------------------------------------------------	
#	EnergyScope TD is an open-source energy model suitable for country scale analysis. It is a simplified representation of an urban or national energy system accounting for the energy flows
#	within its boundaries. Based on a hourly resolution, it optimises the design and operation of the energy system while minimizing the cost of the system.
#	
#	Copyright (C) <2018-2019> <Ecole Polytechnique Fédérale de Lausanne (EPFL), Switzerland and Université catholique de Louvain (UCLouvain), Belgium>
#	
#	Licensed under the Apache License, Version 2.0 (the "License";
#	you may not use this file except in compliance with the License.
#	You may obtain a copy of the License at
#	
#		http://www.apache.org/licenses/LICENSE-2.0
#	
#	Unless required by applicable law or agreed to in writing, software
#	distributed under the License is distributed on an "AS IS" BASIS,
#	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#	See the License for the specific language governing permissions and
#	limitations under the License.
#	
#	Description and complete License: see LICENSE file.
# -------------------------------------------------------------------------------------------------------------------------		


#########################
###  SETS [Figure ...]  ###
#########################

## MAIN SETS: Sets whose elements are input directly in the data file
set PERIODS := 1 .. 8760; # time periods (hours of the year)
set HOURS := 1 .. 24; # hours of the day
set TYPICAL_DAYS:= 1 .. 12; # typical days
set T_H_TD within {PERIODS, HOURS, TYPICAL_DAYS}; # set linking periods, hours, days, typical days
set SECTORS; # sectors of the energy system
set END_USES_INPUT; # Types of demand (end-uses). Input to the model
set END_USES_CATEGORIES; # Categories of demand (end-uses): electricity, heat, mobility
set END_USES_TYPES_OF_CATEGORY {END_USES_CATEGORIES}; # Types of demand (end-uses).
set RESOURCES; # Resources: fuels (wood and fossils) and electricity imports + added GL : RES
set BIOFUELS within RESOURCES; # imported biofuels.
set EXPORT within RESOURCES; # exported resources
set END_USES_TYPES := setof {i in END_USES_CATEGORIES, j in END_USES_TYPES_OF_CATEGORY [i]} j; # secondary set
set TECHNOLOGIES_OF_END_USES_TYPE {END_USES_TYPES}; # set all energy conversion technologies (excluding storage technologies)
set STORAGE_TECH; #  set of storage technologies 
set STORAGE_OF_END_USES_TYPES    {END_USES_TYPES} within STORAGE_TECH; # set all storage technologies related to an end uses types (used for thermal solar (TS))
set INFRASTRUCTURE; # Infrastructure: DHN, grid, and intermediate energy conversion technologies (i.e. not directly supplying end-use demand)
set REGIONS; # Regions that are considered for the Italian energy system
set EXCHANGE; #Exchange of resources among regions

## SECONDARY SETS: a secondary set is defined by operations on MAIN SETS
set LAYERS := (RESOURCES diff BIOFUELS diff EXPORT) union END_USES_TYPES; # Layers are used to balance resources/products in the system
set TECHNOLOGIES := (setof {i in END_USES_TYPES, j in TECHNOLOGIES_OF_END_USES_TYPE [i]} j) union STORAGE_TECH union INFRASTRUCTURE; 
set TECHNOLOGIES_OF_END_USES_CATEGORY {i in END_USES_CATEGORIES} within TECHNOLOGIES := setof {j in END_USES_TYPES_OF_CATEGORY[i], k in TECHNOLOGIES_OF_END_USES_TYPE [j]} k;
set RE_RESOURCES within RESOURCES; # Exhaustive list of RE resources (including wind hydro solar), used to compute the RE share
set V2G within TECHNOLOGIES;   # EVs which can be used for vehicle-to-grid (V2G).
set EVs_BATT   within STORAGE_TECH; # specific battery of EVs
set EVs_BATT_OF_V2G {V2G}; # Makes the link between batteries of EVs and the V2G technology
set STORAGE_DAILY within STORAGE_TECH;# Storages technologies for daily application 
set TS_OF_DEC_TECH {TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}} ; # Makes the link between TS and the technology producing the heat

##Additional SETS added just to simplify equations.
set TYPICAL_DAY_OF_PERIOD {t in PERIODS} := setof {h in HOURS, td in TYPICAL_DAYS: (t,h,td) in T_H_TD} td; #TD_OF_PERIOD(T)
set HOUR_OF_PERIOD {t in PERIODS} := setof {h in HOURS, td in TYPICAL_DAYS: (t,h,td) in T_H_TD} h; #H_OF_PERIOD(T)

## Additional SETS: only needed for printing out results
set COGEN within TECHNOLOGIES; # cogeneration tech
set BOILERS within TECHNOLOGIES; # boiler tech


#################################
### PARAMETERS [Tables ...]   ###
#################################

## Parameters added to include time series in the model [Table ...]
param electricity_time_serie {HOURS, TYPICAL_DAYS, REGIONS} >= 0, <= 1; # %_elec: factor for sharing lighting across typical days (adding up to 1)
param heating_time_serie {HOURS, TYPICAL_DAYS, REGIONS} >= 0, <= 1; # %_sh: factor for sharing space heating across typical days (adding up to 1)
param cooling_time_serie {HOURS, TYPICAL_DAYS, REGIONS} >= 0, <= 1; # %_sc: factor for sharing space cooling across typical days (adding up to 1)
param mob_pass_time_serie {HOURS, TYPICAL_DAYS} >= 0, <= 1; # %_pass: factor for sharing passenger transportation across Typical days (adding up to 1) based on https://www.fhwa.dot.gov/policy/2013cpr/chap1.cfm
param mob_freight_time_serie {HOURS, TYPICAL_DAYS} >= 0, <= 1; # %_fr: factor for sharing freight transportation across Typical days (adding up to 1)
param c_p_t {TECHNOLOGIES, HOURS, TYPICAL_DAYS, REGIONS} default 1; #Hourly capacity factor. If equal to 1 <=> no impact.

## Parameters added to define scenarios [Table ...]
param end_uses_demand_year_r {END_USES_INPUT, SECTORS, REGIONS} >= 0 default 0; # end_uses_year: table regional end-uses demand vs sectors (input to the model). Yearly values.
param end_uses_input {i in END_USES_INPUT, r in REGIONS} := sum {s in SECTORS} (end_uses_demand_year_r [i,s,r]); # Figure 1.4: total demand for each type of end-uses across sectors (yearly energy) as input from the demand-side model
param i_rate > 0; # discount rate (real discount rate)

# parameter tau is defined later because it requires some technical data.
param re_share_primary >= 0; # re_share: minimum share of primary energy coming from RE (>20%)
param gwp_limit >= 0;    # [ktCO2-eq./year] maximum gwp emissions allowed. CO2 emission in 2015 (305040 ktCO2)

param share_mobility_public_min >= 0, <= 1; # %_public,min: min limit for penetration of public mobility over total mobility 
param share_mobility_public_max >= 0, <= 1; # %_public,max: max limit for penetration of public mobility over total mobility 

param share_freight_train_min >= 0, <= 1; # %_rail,min: min limit for penetration of train in freight transportation
param share_freight_train_max >= 0, <= 1; # %_rail,min: max limit for penetration of train in freight transportation

param share_heat_dhn_min {REGIONS}>= 0, <= 1; # %_dhn,min: min limit for penetration of dhn in low-T heating
param share_heat_dhn_max {REGIONS}>= 0, <= 1; # %_dhn,max: max limit for penetration of dhn in low-T heating

param t_op {HOURS, TYPICAL_DAYS} default 1; 
param f_max {TECHNOLOGIES, REGIONS} >= 0; # Maximum feasible installed capacity [GW], refers to main output. storage level [GWh] for STORAGE_TECH
param f_min {TECHNOLOGIES, REGIONS} >= 0; # Minimum feasible installed capacity [GW], refers to main output. storage level [GWh] for STORAGE_TECH
param fmax_perc {TECHNOLOGIES, REGIONS} >= 0, <= 1 default 1; # value in [0,1]: this is to fix that a technology can at max produce a certain % of the total output of its sector over the entire year
param fmin_perc {TECHNOLOGIES, REGIONS} >= 0, <= 1 default 0; # value in [0,1]: this is to fix that a technology can at min produce a certain % of the total output of its sector over the entire year

param avail {RESOURCES, REGIONS} >= 0; # Yearly availability of resources [GWh/y]
param c_op {RESOURCES} >= 0; # cost of resources in the different periods [MCHF/GWh]
param n_car_max >=0; #  [car] Maximum amount of cars
param peak_sh_factor >= 0;   # %_Peak_sh: ratio between highest yearly demand and highest TDs demand

## Parameters added to define technologies [Table ...]:
param layers_in_out {RESOURCES union TECHNOLOGIES diff STORAGE_TECH , LAYERS}; # f: input/output Resources/Technologies to Layers. Reference is one unit ([GW] or [Mpkm/h] or [Mtkm/h]) of (main) output of the resource/technology. input to layer (output of technology) > 0.
param c_inv {TECHNOLOGIES} >= 0; # Specific investment cost [MCHF/GW].[MCHF/GWh] for STORAGE_TECH
param c_maint {TECHNOLOGIES} >= 0; # O&M cost [MCHF/GW/year]: O&M cost does not include resource (fuel) cost. [MCHF/GWh/year] for STORAGE_TECH
param lifetime {TECHNOLOGIES} >= 0; # n: lifetime [years]
param tau {i in TECHNOLOGIES} := i_rate * (1 + i_rate)^lifetime [i] / (((1 + i_rate)^lifetime [i]) - 1); # Annualisation factor for each different technology [Eq. 2]
param gwp_constr {TECHNOLOGIES} >= 0; # GWP emissions associated to the construction of technologies [ktCO2-eq./GW]. Refers to [GW] of main output
param gwp_op {RESOURCES} >= 0; # GWP emissions associated to the use of resources [ktCO2-eq./GWh]. Includes extraction/production/transportation and combustion
param c_p {TECHNOLOGIES, REGIONS} >= 0, <= 1 default 1; # yearly capacity factor of each technology, defined on annual basis. Different than 1 if sum {t in PERIODS} F_t (t) <= c_p * F
param storage_eff_in {STORAGE_TECH , LAYERS} >= 0, <= 1; # eta_sto_in: efficiency of input to storage from layers.  If 0 storage_tech/layer are incompatible
param storage_eff_out {STORAGE_TECH , LAYERS} >= 0, <= 1; # eta_sto_out: efficiency of output from storage to layers. If 0 storage_tech/layer are incompatible
param storage_losses {STORAGE_TECH} >= 0, <= 1; # %_sto_loss : Self losses in storage (required for Li-ion batteries). Value = self discharge in 1 hour.
param storage_charge_time    {STORAGE_TECH} >= 0; # [h]. t_sto_in: Time to charge storage (Energy to Power ratio). If value =  5 <=>  5h for a full charge.
param storage_discharge_time {STORAGE_TECH} >= 0; # [h]. t_sto_out: Time to discharge storage (Energy to Power ratio). If value =  5 <=>  5h for a full discharge.
param storage_availability {STORAGE_TECH} >=0, default 1;# %_sto_avail: Storage technology availability to charge/discharge. Used for EVs 
param loss_network {END_USES_TYPES} >= 0 default 0; #%_net_loss: Losses coefficient [0; 1] in the networks (grid and DHN)
param Batt_per_Car {V2G} >= 0; # ev_Batt_size: [GWh] Battery size per EVs car technology
param c_grid_extra >=0; # Cost to reinforce the grid due to IRE penetration


##Additional parameter 
param total_time := sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (t_op [h, td]); # added just to simplify equations


#################################
###   VARIABLES [Tables ...]  ###
#################################

##Independent variables [Table ...] :
var Share_Mobility_Public >= share_mobility_public_min, <= share_mobility_public_max; # %_Public: Ratio [0; 1] public mobility over total passenger mobility
var Share_Freight_Train, >= share_freight_train_min, <= share_freight_train_max; # %_Rail: Ratio [0; 1] rail transport over total freight transport
var Share_Heat_Dhn{r in REGIONS}, >= share_heat_dhn_min[r], <= share_heat_dhn_max[r]; # %_DHN: Ratio [0; 1] centralized over total low-temperature heat
var F {TECHNOLOGIES, REGIONS} >= 0; # F: Installed capacity with respect to main output (see layers_in_out)
var F_t {RESOURCES union TECHNOLOGIES, HOURS, TYPICAL_DAYS, REGIONS} >= 0; # F_t: Operation in each period. multiplication factor with respect to the values in layers_in_out table. Takes into account c_p
var Storage_in {i in STORAGE_TECH, LAYERS, HOURS, TYPICAL_DAYS, REGIONS} >= 0; # Sto_in: Power [GW] input to the storage in a certain period
var Storage_out {i in STORAGE_TECH, LAYERS, HOURS, TYPICAL_DAYS, REGIONS} >= 0; # Sto_out: Power [GW] output from the storage in a certain period
var Power_nuclear  >=0; # [GW] P_Nuc: Constant load of nuclear
var Shares_Mobility_Passenger {TECHNOLOGIES_OF_END_USES_CATEGORY["MOBILITY_PASSENGER"], r in REGIONS} >=0; # %_MobPass: Constant share of mobility passenger
var Shares_LowT_Dec {TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, r in REGIONS}>=0 ; # %_HeatDec: Constant share of heat Low T decentralised + its specific thermal solar
var F_Solar         {TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, r in REGIONS} >=0; # [GW] F_sol: Solar thermal installed capacity per heat decentralised technologies
var F_t_Solar       {TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, h in HOURS, td in TYPICAL_DAYS, r in REGIONS} >= 0; #[GW] F_t_sol: Solar thermal operating per heat decentralised technologies

var ship {LAYERS, HOURS, TYPICAL_DAYS, r in REGIONS, r2 in REGIONS:r <> r2}; # resources transfer from one region (r) to another (r2)

##Dependent variables [Table ...] :
var End_Uses {LAYERS, HOURS, TYPICAL_DAYS, REGIONS} >= 0; #EndUses: total demand for each type of end-uses (hourly power). Defined for all layers (0 if not demand)
var TotalCost >= 0; # [ktCO2-eq/year] C_tot: Total GWP emissions in the system [ktCO2-eq./y]
var C_inv {TECHNOLOGIES, REGIONS} >= 0; #C_inv: [MCHF] Total investment cost of each technology
var C_maint {TECHNOLOGIES, REGIONS} >= 0; #C_maint: [MCHF/year] Total O&M cost of each technology (excluding resource cost)
var C_op {RESOURCES, REGIONS} >= 0; #C_op [MCHF/year] Total O&M cost of each resource
var TotalGWP >= 0; # [ktCO2-eq/year] GWP_tot: Total global warming potential (GWP) emissions in the system [ktCO2-eq./y]
var TotalGWP_op >=0;
var GWP_constr {TECHNOLOGIES, REGIONS} >= 0; # [ktCO2-eq] GWP_constr: Total emissions of the technologies [ktCO2-eq.]
var GWP_op {RESOURCES, REGIONS} >= 0; #  [ktCO2-eq] GWP_op: Total yearly emissions of the resources [ktCO2-eq./y]
var Network_losses {END_USES_TYPES, HOURS, TYPICAL_DAYS, REGIONS} >= 0; # Net_loss [GW]: Losses in the networks (normally electricity grid and DHN)
var Storage_level {STORAGE_TECH, PERIODS, REGIONS} >= 0; # Sto_level: [GWh] Energy stored at each period
var TotalGWP_r {REGIONS} >= 0; # GWP_tot: Total global warming potential (GWP) emissions in the system [ktCO2-eq./y]
var TotalCost_r {REGIONS}>= 0; # C_tot: Total GWP emissions in the system [ktCO2-eq./y]



#########################################
###      CONSTRAINTS Eqs [...]       ###
#########################################

# Echanges between regions

# Allowing transportation of RESOURCES (Elec.) from one region to another.
subject to ship_in_negatif {l in LAYERS, h in HOURS, td in TYPICAL_DAYS, r in REGIONS, r2 in REGIONS: r <> r2}:
	ship [l,h,td,r,r2] = - ship [l,h,td,r2,r]; 

subject to stop_ship_not_wanted {l in LAYERS diff EXCHANGE, h in HOURS, td in TYPICAL_DAYS, r in REGIONS, r2 in REGIONS: r <> r2}:
	ship [l,h,td,r,r2]  = 0;


## End-uses demand calculation constraints 
#-----------------------------------------


# From annual energy demand to hourly power demand. End_Uses is non-zero only for demand layers.
subject to end_uses_t {l in LAYERS, h in HOURS, td in TYPICAL_DAYS, r in REGIONS}:
	End_Uses [l, h, td, r] = (if l == "ELECTRICITY" 
		then
			(end_uses_input[l,r] / total_time + end_uses_input["LIGHTING",r] * electricity_time_serie [h, td, r] / t_op [h, td] ) + Network_losses [l,h,td,r]
		else (if l == "HEAT_LOW_T_DHN" then
			(end_uses_input["HEAT_LOW_T_HW",r] / total_time + end_uses_input["HEAT_LOW_T_SH",r] * heating_time_serie [h, td, r] / t_op [h, td] ) * Share_Heat_Dhn[r] + Network_losses [l,h,td,r]
		else (if l == "HEAT_LOW_T_DECEN" then
			(end_uses_input["HEAT_LOW_T_HW",r] / total_time + end_uses_input["HEAT_LOW_T_SH",r] * heating_time_serie [h, td, r] / t_op [h, td] ) * (1 - Share_Heat_Dhn[r])
		else (if l == "MOB_PUBLIC" then
			(end_uses_input["MOBILITY_PASSENGER",r] * mob_pass_time_serie [h, td] / t_op [h, td]  ) * Share_Mobility_Public
		else (if l == "MOB_PRIVATE" then
			(end_uses_input["MOBILITY_PASSENGER",r] * mob_pass_time_serie [h, td] / t_op [h, td]  ) * (1 - Share_Mobility_Public)
		else (if l == "MOB_FREIGHT_RAIL" then
			(end_uses_input["MOBILITY_FREIGHT",r]   * mob_freight_time_serie [h, td] / t_op [h, td] ) *  Share_Freight_Train
		else (if l == "MOB_FREIGHT_ROAD" then
			(end_uses_input["MOBILITY_FREIGHT",r]   * mob_freight_time_serie [h, td] / t_op [h, td] ) *(1 - Share_Freight_Train)
		else (if l == "HEAT_HIGH_T" then
			end_uses_input["HEAT_HIGH_T",r] / total_time
		else (if l == "COLD_PRO" then
			end_uses_input["COLD_PRO",r] / total_time
		else (if l == "COLD_SC" then
			end_uses_input[l,r] * cooling_time_serie [h, td, r] / t_op [h, td]
		else (if l == "MOBILITY_FARMING" then
			end_uses_input["MOBILITY_FARMING",r] / total_time
		else 
			0 ))))))))))); # For all layers which don't have an end-use demand
	
## Cost
#------

# [Eq. ...] Investment cost of each technology
subject to investment_cost_calc {j in TECHNOLOGIES, r in REGIONS}: # add storage investment cost
	C_inv [j,r] = c_inv [j] * F [j,r];
		
# [Eq. ...] O&M cost of each technology
subject to main_cost_calc {j in TECHNOLOGIES, r in REGIONS}: # add storage investment
	C_maint [j,r] = c_maint [j] * F [j,r];		

# [Eq. ...] Total cost of each resource
subject to op_cost_calc {i in RESOURCES, r in REGIONS}:
	C_op [i,r] = sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (c_op [i] * F_t [i, h, td,r] * t_op [h, td] ) ;

# [Eq. ...]	
subject to totalcost_cal_r {r in REGIONS}:
	TotalCost_r [r] = sum {i in TECHNOLOGIES} (tau [i]  * C_inv [i, r] + C_maint [i, r]) + sum {j in RESOURCES} C_op [j, r];
	
subject to totalcost_cal:
	TotalCost = sum {r in REGIONS} (TotalCost_r [r]);
	
	
## Emissions
#-----------


# [Eq. ...]
subject to gwp_op_calc {i in RESOURCES, r in REGIONS}:
	GWP_op [i,r] = gwp_op [i] * sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} ( F_t [i, h, td, r] * t_op [h, td] );	
	
# [Eq. ...]
subject to totalGWP_calc_r {r in REGIONS}:
	TotalGWP_r [r] = sum {j in RESOURCES} GWP_op [j, r];

# [Eq. ...]
subject to totalGWP_calc:
	TotalGWP = sum {r in REGIONS} (TotalGWP_r[r]);
	
	
## Multiplication factor
#-----------------------
	
# [Eq. ...] min & max limit to the size of each technology
subject to size_limit {j in TECHNOLOGIES, r in REGIONS}:
	f_min [j,r] <= F [j,r] <= f_max [j,r];
	
# [Eq. ...] relation between power and capacity via period capacity factor. This forces max hourly output (e.g. renewables)
subject to capacity_factor_t {j in TECHNOLOGIES, h in HOURS, td in TYPICAL_DAYS, r in REGIONS}:
	F_t [j, h, td, r] <= F [j,r] * c_p_t [j, h, td, r];
	
# [Eq. ...] relation between mult_t and mult via yearly capacity factor. This one forces total annual output
subject to capacity_factor {j in TECHNOLOGIES, r in REGIONS}:
	sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t [j, h, td, r] * t_op [h, td]) <= F [j,r] * c_p [j,r] * total_time;	
		
## Resources
#-----------
# [Eq. ...] Availability of regional resources
subject to resource_availability {i in RESOURCES, r in REGIONS}:
	sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (F_t [i, h, td, r] * t_op [h, td]) <= avail [i, r];
	
## Layers
#--------

# [Eq. ...] Layer balance equation with storage. Layers: input > 0, output < 0. Demand > 0. Storage: in > 0, out > 0;
# output from technologies/resources/storage - input to technologies/storage = demand. Demand has default value of 0 for layers which are not end_uses
subject to layer_balance {l in LAYERS, h in HOURS, td in TYPICAL_DAYS, r in REGIONS}:
		sum {i in RESOURCES union TECHNOLOGIES diff STORAGE_TECH } 
		(layers_in_out[i, l] * F_t [i, h, td, r]) 
		+ sum {j in STORAGE_TECH} ( Storage_out [j, l, h, td, r] - Storage_in [j, l, h, td, r] )
		- End_Uses [l, h, td, r]
		- sum{r2 in REGIONS: r <> r2} (ship[l,h,td,r,r2])
		= 0;
	
## Storage	
#---------
	
# [Eq. ...] The level of the storage represents the amount of energy stored at a certain time.
subject to storage_level {j in STORAGE_TECH, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}:
	Storage_level [j, t, r] = (if t == 1 then
	 			Storage_level [j, card(PERIODS), r] * (1.0 -  storage_losses[j])
				+ t_op [h, td] * (   (sum {l in LAYERS: storage_eff_in [j,l] > 0}  (Storage_in [j, l, h, td, r]  * storage_eff_in  [j, l])) 
				                   - (sum {l in LAYERS: storage_eff_out [j,l] > 0} (Storage_out [j, l, h, td, r] / storage_eff_out [j, l])))
	else
	 			Storage_level [j, t-1, r] * (1.0 -  storage_losses[j])
				+ t_op [h, td] * (   (sum {l in LAYERS: storage_eff_in [j,l] > 0}  (Storage_in [j, l, h, td, r]  * storage_eff_in  [j, l])) 
				                   - (sum {l in LAYERS: storage_eff_out [j,l] > 0} (Storage_out [j, l, h, td, r] / storage_eff_out [j, l])))
				);

# [Eq. ...] Bounding daily storage
subject to impose_daily_storage {j in STORAGE_DAILY, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}:
	Storage_level [j, t, r] = F_t [j, h, td, r];
	
# [Eq. ...] Bounding seasonal storage
subject to limit_energy_stored_to_maximum {j in STORAGE_TECH diff STORAGE_DAILY , t in PERIODS, r in REGIONS}:
	Storage_level [j, t, r] <= F [j,r];# Never exceed the energy stored
	
# [Eqs. ...] Each storage technology can have input/output only to certain layers. If incompatible then the variable is set to 0
subject to storage_layer_in {j in STORAGE_TECH, l in LAYERS, h in HOURS, td in TYPICAL_DAYS, r in REGIONS}:
	Storage_in [j, l, h, td, r] * (ceil (storage_eff_in [j, l]) - 1) = 0;
subject to storage_layer_out {j in STORAGE_TECH, l in LAYERS, h in HOURS, td in TYPICAL_DAYS, r in REGIONS}:
	Storage_out [j, l, h, td, r] * (ceil (storage_eff_out [j, l]) - 1) = 0;
		
# [Eq. ...] limit the Energy to power ratio. 
subject to limit_energy_to_power_ratio {j in STORAGE_TECH , l in LAYERS, h in HOURS, td in TYPICAL_DAYS, r in REGIONS}:
	Storage_in [j, l, h, td, r] * storage_charge_time[j] + Storage_out [j, l, h, td, r] * storage_discharge_time[j] <=  F [j, r] * storage_availability[j];

## Infrastructure
#----------------

# [Eq. ...] Calculation of losses for each end-use demand type (normally for electricity and DHN)
subject to network_losses {eut in END_USES_TYPES, h in HOURS, td in TYPICAL_DAYS, r in REGIONS}:
	Network_losses [eut,h,td,r] = (sum {j in RESOURCES union TECHNOLOGIES diff STORAGE_TECH: layers_in_out [j, eut] > 0} ((layers_in_out[j, eut]) * F_t [j, h, td, r])) * loss_network [eut];

# [Eq. ...] This is the extra investment needed if there is a big deployment of stochastic renewables
subject to extra_grid {r in REGIONS}:
	F ["GRID",r] = 1 + (c_grid_extra / c_inv["GRID"]) * (F ["WIND", r] + F ["PV", r]) / (f_max ["WIND", r] + f_max ["PV", r])  ;

#  [Eq. ...] Valid only for Italian Case study: phase-out of coal requires investments in electric grid and other additional costs.
subject to extra_grid1 {r in REGIONS}:
	F ["GRID_COAL",r] = 1 - (F ["COAL_US", r]) / (f_max ["COAL_US", r])  ;


# [Eq. ...] DHN: assigning a cost to the network
subject to extra_dhn {r in REGIONS}:
	F ["DHN", r] = sum {j in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DHN"]} (F [j, r]);

# [Eq. ...] Power2Gas investment cost is calculated on the max size of the two units
subject to Power2gas_1 {r in REGIONS}:
	F ["POWER2GAS", r] >= F ["POWER2GAS_in", r];
subject to Power2gas_2 {r in REGIONS}:
	F ["POWER2GAS", r] >= F ["POWER2GAS_out", r];	
	
	
## Additional constraints
#------------------------

# [Eq. ...] Operating strategy in private mobility (to make model more realistic)
# Each passenger mobility technology (j) has to supply a constant share  (Shares_Mobility_Passenger[j])of the passenger mobility demand
subject to operating_strategy_mob_private{j in TECHNOLOGIES_OF_END_USES_CATEGORY["MOBILITY_PASSENGER"], h in HOURS, td in TYPICAL_DAYS, r in REGIONS}:
	F_t [j, h, td, r]   = Shares_Mobility_Passenger [j, r] * (end_uses_input["MOBILITY_PASSENGER", r] * mob_pass_time_serie [h, td] / t_op [h, td] );
	
## Thermal solar & thermal storage:

# [Eq. ...] relation between decentralised thermal solar power and capacity via period capacity factor.
subject to thermal_solar_capacity_factor {j in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, h in HOURS, td in TYPICAL_DAYS, r in REGIONS}:
	F_t_Solar [j, h, td, r] <= F_Solar[j, r] * c_p_t["DEC_SOLAR", h, td, r];
	
# [Eq. ...] Overall thermal solar is the sum of specific thermal solar 	
subject to thermal_solar_total_capacity {r in REGIONS}:
	F ["DEC_SOLAR", r] = sum {j in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}} F_Solar[j, r];

# [Eq. ...]: Decentralised thermal technology must supply a constant share of heat demand.
subject to decentralised_heating_balance  {j in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, i in TS_OF_DEC_TECH[j], h in HOURS, td in TYPICAL_DAYS, r in REGIONS}:
	F_t [j, h, td, r] + F_t_Solar [j, h, td, r] + sum {l in LAYERS } ( Storage_out [i, l, h, td, r] - Storage_in [i, l, h, td, r])  
		= Shares_LowT_Dec[j, r] * (end_uses_input["HEAT_LOW_T_HW", r] / total_time + end_uses_input["HEAT_LOW_T_SH", r] * heating_time_serie [h, td, r] / t_op [h, td]);


## EV storage :

# [Eq. ...] Compute the equivalent size of V2G batteries based on the share of V2G, the amount of cars and the battery capacity per EVs technology
subject to EV_storage_size {j in V2G, i in EVs_BATT_OF_V2G[j], r in REGIONS}:
	F [i, r] = n_car_max * Shares_Mobility_Passenger[j, r] * Batt_per_Car[j];# Battery size proportional to the amount of cars
	
# [Eq. ...]  Impose EVs to be supplied by their battery.
subject to EV_storage_for_V2G_demand {j in V2G, i in EVs_BATT_OF_V2G[j], h in HOURS, td in TYPICAL_DAYS, r in REGIONS}:
	Storage_out [i,"ELECTRICITY",h,td, r] >=  - layers_in_out[j,"ELECTRICITY"]* F_t [j, h, td, r];
		
## Peak demand :

# [Eq. ...] Peak in decentralized heating
subject to peak_lowT_dec {j in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, h in HOURS, td in TYPICAL_DAYS, r in REGIONS}:
	F [j, r] >= peak_sh_factor * F_t [j, h, td, r] ;

# [Eq. ...] Calculation of max heat demand in DHN (1st constrain required to linearised the max function)
var Max_Heat_Demand {REGIONS}>= 0;
subject to max_dhn_heat_demand {h in HOURS, td in TYPICAL_DAYS, r in REGIONS}:
	Max_Heat_Demand [r]>= End_Uses ["HEAT_LOW_T_DHN", h, td, r];
	
# [Eq. ...] Peak in DHN
subject to peak_lowT_dhn {r in REGIONS}:
	sum {j in TECHNOLOGIES_OF_END_USES_TYPE ["HEAT_LOW_T_DHN"], i in STORAGE_OF_END_USES_TYPES["HEAT_LOW_T_DHN"]} (F [j, r] + F[i, r]/storage_discharge_time[i]) >= peak_sh_factor * Max_Heat_Demand[r];
	

## Adaptation for the case study: Constraints added for the application to Italy
#-----------------------------------------------------------------------------------------------------------------------

# [Eq. ...]  constraint to reduce the GWP subject to Minimum_gwp_reduction :
subject to Minimum_GWP_reduction :
	TotalGWP <= gwp_limit;

# [Eq. ...] Minimum share of RE in primary energy supply
subject to Minimum_RE_share :
	sum {j in RE_RESOURCES, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} F_t [j, h, td, r] * t_op [h, td] + sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} (F_t ["WASTE", h, td, r] * t_op [h, td])/2
	>=	re_share_primary *
	sum {j in RESOURCES, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} F_t [j, h, td, r] * t_op [h, td];

	
# [Eq. ...] Definition of min/max output of each technology as % of total output in a given layer. 
subject to f_max_perc {eut in END_USES_TYPES, j in TECHNOLOGIES_OF_END_USES_TYPE[eut], r in REGIONS}:
	sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (F_t [j,h,td,r] * t_op[h,td]) <= fmax_perc [j,r] * sum {j2 in TECHNOLOGIES_OF_END_USES_TYPE[eut], t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (F_t [j2, h, td, r] * t_op[h,td]);
subject to f_min_perc {eut in END_USES_TYPES, j in TECHNOLOGIES_OF_END_USES_TYPE[eut], r in REGIONS}:
	sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (F_t [j,h,td, r] * t_op[h,td]) >= fmin_perc [j,r] * sum {j2 in TECHNOLOGIES_OF_END_USES_TYPE[eut], t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (F_t [j2, h, td, r] * t_op[h,td]);

# [Eq. ...] Energy efficiency is a fixed cost
subject to extra_efficiency {r in REGIONS}:
	F ["EFFICIENCY", r] = 1 / (1 + i_rate);	


##########################
### OBJECTIVE FUNCTION ###
##########################

# Can choose between TotalGWP and TotalCost
minimize obj: TotalCost
;

solve;

## Print total yearly output to txt file

printf "%s\t%s\t%s\t%s\n", "Name", "Output NO", "Output SO", "Output CN" > "output/total_output.txt"; 
for {i in TECHNOLOGIES union RESOURCES}{
		printf "%s", i >> "output/total_output.txt";
		for {r in REGIONS}{
		printf "\t%.3f", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (F_t [i, h, td, r] * t_op [h, td]) >> "output/total_output.txt";
        }
        printf "\n" >> "output/total_output.txt";
        }


#------------------------------------------
## Print total yearly output to txt file (no Regions).
#------------------------------------------


## Print total yearly output to txt file

printf "%s\t%s\n", "Name",  "Yearly output" > "output/total_output_TOT.txt"; 
for {i in TECHNOLOGIES union RESOURCES}{
		printf "%s\t%.3f\n", i, 
		sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} (F_t [i, h, td, r] * t_op [h, td]) >> "output/total_output_TOT.txt";
}

#------------------------------------------
## Print hourly PV+Wind output to txt file (no Regions).
#------------------------------------------

## Print total yearly output to txt file

printf "%s\t%s\n", "Hour",  "PV Output" > "output/PV_output_TOT.txt"; 
for {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]}{
		printf "%s\t%.3f\n", h, 
		sum{r in REGIONS} (F_t ["PV", h, td, r] * t_op [h, td] + F_t ["WIND", h, td, r] * t_op [h, td]) >> "output/PV_output_TOT.txt";
}


#------------------------------------------
## Print hourly PV output to txt file (no Regions).
#------------------------------------------


## Print total yearly output to txt file

printf "%s\t%s\n", "Hour",  "Elec Demand" > "output/Elec_output_TOT.txt"; 
for {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]}{
		printf "%s\t%.3f\n", h, 
		sum{r in REGIONS} (End_Uses ["ELECTRICITY", h, td, r] -layers_in_out["FARM_MACHINE","ELECTRICITY"] * F_t ["FARM_MACHINE", h, td, r]  -layers_in_out["MOTOCYCLE","ELECTRICITY"] * F_t ["MOTOCYCLE", h, td, r]  -layers_in_out["IND_DIRECT_ELEC","HEAT_HIGH_T"] * F_t ["IND_DIRECT_ELEC", h, td, r]  -layers_in_out["H2_ELECTROLYSIS","ELECTRICITY"] * F_t ["H2_ELECTROLYSIS", h, td, r]  -layers_in_out["DEC_ELEC_COLD","ELECTRICITY"] * F_t ["DEC_ELEC_COLD", h, td, r]   - layers_in_out["IND_ELEC_COLD","ELECTRICITY"] * F_t ["IND_ELEC_COLD", h, td, r]  -Network_losses ["ELECTRICITY", h, td, r]   -layers_in_out["DHN_HP_ELEC","ELECTRICITY"] * F_t ["DHN_HP_ELEC", h, td, r]   - layers_in_out["DEC_HP_ELEC","ELECTRICITY"] * F_t ["DEC_HP_ELEC", h, td, r]  - layers_in_out["ELEC_EXPORT","ELECTRICITY"] * F_t ["ELEC_EXPORT", h, td, r]  -layers_in_out["TRAIN_FREIGHT","ELECTRICITY"] * F_t ["TRAIN_FREIGHT", h, td, r] -layers_in_out["TRAIN_PUB","ELECTRICITY"] * F_t ["TRAIN_PUB", h, td, r]   - layers_in_out["TRAMWAY_TROLLEY","ELECTRICITY"] * F_t ["TRAMWAY_TROLLEY", h, td, r]  -layers_in_out["CAR_PHEV","ELECTRICITY"] * F_t ["CAR_PHEV", h, td, r]   - layers_in_out["CAR_BEV","ELECTRICITY"] * F_t ["CAR_BEV", h, td, r]) >> "output/Elec_output_TOT.txt";
}


## Print total yearly output to txt file

printf "%s\t%s\n", "Hour",  "Dam" > "output/Dam_output_TOT.txt"; 
for {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]}{
		printf "%s\t%.3f\n", h, 
		sum{r in REGIONS}(-Storage_in ["DAM_STORAGE", "ELECTRICITY", h, td, r] * storage_eff_in ["DAM_STORAGE", "ELECTRICITY"]) >> "output/Dam_output_TOT.txt";
}


#------------------------------------------
## Print cost breakdown to txt file.
#------------------------------------------


printf "%s\t%s\t%s\t%s\t%s\n", "Name", "REGIONS", "C_inv", "C_maint", "C_op" > "output/cost_breakdown.txt"; 
for {i in TECHNOLOGIES union RESOURCES, r in REGIONS}{
		printf "%s\t%s\t%.6f\t%.6f\t%.6f\n", i,r,  
		if i in TECHNOLOGIES then (tau [i] * C_inv [i, r]) else 0, 
		if i in TECHNOLOGIES then C_maint [i, r] else 0, 
		if i in RESOURCES then C_op [i, r] else 0 >> "output/cost_breakdown.txt";
}

printf "%s\t%s\t%s\t%s\n", "Name", "C_inv", "C_maint", "C_op" > "output/cost_breakdown_TOT.txt"; 
for {i in TECHNOLOGIES union RESOURCES}{
		printf "%s\t%.6f\t%.6f\t%.6f\n", i,  
		if i in TECHNOLOGIES then sum {r in REGIONS}(tau [i] * C_inv [i, r]) else 0, 
		if i in TECHNOLOGIES then sum {r in REGIONS} (C_maint [i, r]) else 0, 
		if i in RESOURCES then sum {r in REGIONS} C_op [i, r] else 0 >> "output/cost_breakdown_TOT.txt";
}


#------------------------------------------
## Print GWP breakdown
#------------------------------------------
printf "%s\t%s\t%s\t%s\n", "Name", "REGIONS", "GWP_constr", "GWP_op" > "output/gwp_breakdown.txt"; 
for {i in TECHNOLOGIES union RESOURCES diff STORAGE_TECH, r in REGIONS}{
		printf "%s\t%s\t%.6f\t%.6f\n", i, r,
		if i in TECHNOLOGIES then (GWP_constr [i, r] / lifetime[i]) else 0,
	    if i in RESOURCES    then GWP_op [i, r] else 0 >> "output/gwp_breakdown.txt";
}

printf "%s\t%s\t%s\n", "Name", "GWP_constr", "GWP_op" > "output/gwp_breakdown_TOT.txt"; 
for {i in TECHNOLOGIES union RESOURCES diff STORAGE_TECH}{
		printf "%s\t%.6f\t%.6f\n", i, 
		if i in TECHNOLOGIES then sum {r in REGIONS}(GWP_constr [i, r] / lifetime[i]) else 0,
	    if i in RESOURCES    then sum {r in REGIONS} GWP_op [i, r] else 0 >> "output/gwp_breakdown_TOT.txt";
}


## Print F_Mult to txt file
printf "%s\t%s\t%s\t%s\t\n", "Name", "NO", "SO", "CN" > "output/F.txt"; 
for {i in TECHNOLOGIES}{
	printf "%s", i >> "output/F.txt";
	for {r in REGIONS}{
		printf "\t%.6f", F[i,r] >> "output/F.txt";
	}
		printf "\n" >> "output/F.txt";
}


## 	Flows in layers, and regions
for {l in LAYERS, r in REGIONS}{
	printf "Td \t Time\t" > ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 
	for {i in RESOURCES union TECHNOLOGIES diff STORAGE_TECH }{
		printf "%s\t", i >> ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 
	}
	for {j in STORAGE_TECH }{
		printf "%s_Pin\t",j >> ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 
		printf "%s_Pout\t",j >> ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 
	}
	for {r2 in REGIONS: r <> r2}{
			printf "ship_in_from_%s\t", r2 >> ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 
			printf "ship_out_to_%s\t", r2 >> ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 
		}
	printf "END_USE\t" >> ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 

	for {td in TYPICAL_DAYS, h in HOURS}{
		printf "\n %d \t %d\t",td,h   >> ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 
		for {i in RESOURCES union TECHNOLOGIES diff STORAGE_TECH}{
			printf "%f\t",(layers_in_out[i, l] * F_t [i, h, td, r]) >> ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 
		}
		for {j in STORAGE_TECH}{
			printf "%f\t",(-Storage_in [j, l, h, td, r]) >> ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 
			printf "%f\t", (Storage_out [j, l, h, td, r])>> ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 
		}
		for {r2 in REGIONS: r <> r2}{
			printf "%f\t", -ship[l,h,td,r,r2] >> ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 
			printf "%f\t", ship[l,h,td,r,r2] >> ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 
		}
		printf "%f\t", -End_Uses [l, h, td, r]  >> ("output/hourly_data/layer_" & l & "_" & r & ".txt"); 
	}
}

## STORAGE distribution CURVES 
# Should add region index
printf "Time\t" > "output/hourly_data/energy_stored.txt";
for {i in STORAGE_TECH }{
	printf "%s\t", i >> "output/hourly_data/energy_stored.txt";
}
for {i in STORAGE_TECH }{
	printf "%s_in\t" , i >> "output/hourly_data/energy_stored.txt";
	printf "%s_out\t", i >> "output/hourly_data/energy_stored.txt";
}
for {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}{
	printf "\n %d\t",t  >> "output/hourly_data/energy_stored.txt";
	for {i in STORAGE_TECH}{
		printf "%f\t", Storage_level[i, t, r] >> "output/hourly_data/energy_stored.txt";
	}
	for {i in STORAGE_TECH}{
		printf "%f\t", (sum {l in LAYERS: storage_eff_in [i,l] > 0}
-(Storage_in [i, l, h, td, r] ))
	>> "output/hourly_data/energy_stored.txt";
		printf "%f\t", (sum {l in LAYERS: storage_eff_in [i,l] > 0}
(Storage_out [i, l, h, td, r] ))
	>> "output/hourly_data/energy_stored.txt";
	}
}

## Print ship_in to txt file in GW
printf "%s\t%s\t%s\n", "Name", "To", "From" > "output/ship_in.txt"; 
for {l in EXCHANGE,r in REGIONS, r2 in REGIONS: r<>r2 and (l =='ELECTRICITY')}{
	printf "%s\t%s\t%s\t",l,r,r2 >> "output/ship_in.txt";
		printf "%.10f\t",
		sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (ship [l,h,td,r,r2]*t_op[h,td])  >> "output/ship_in.txt";
		printf "\n" >> "output/ship_in.txt";
}

## Print ship_out to txt file in GW
printf "%s\t%s\n", "Name", "From" > "output/ship_out.txt"; 
for {l in EXCHANGE, r in REGIONS, r2 in REGIONS: r<>r2 and (l =='ELECTRICITY')}{
	printf "%s\t%s\t%s\t",l,r,r2 >> "output/ship_out.txt";
		printf "%.10f\t", 
		sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (ship [l,h,td,r,r2]*t_op[h,td]) >> "output/ship_out.txt";
		printf "\n" >> "output/ship_out.txt";
}	



##!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!##
##SANKEY : THIS IS A ALPHA VERSION AND MIGHT CONTAIN MISTAKES. TO BE USED CAREFULLY##
##!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!##

# The code to plot the Sankey diagrams is originally taken from: http://bl.ocks.org/d3noob/c9b90689c1438f57d649
# Adapted by the IPESE team

## Generate CSV file to be used as input to Sankey diagram
# Notes:
# - workaround to write if-then-else statements in GLPK: https://en.wikibooks.org/wiki/GLPK/GMPL_Workarounds#If–then–else_conditional
# - to visualize the Sankey, open the html file in any browser. If it does not work, try this: https://threejs.org/docs/#manual/en/introduction/How-to-run-things-locally
# - Power2Gas not included in the diagram
printf "%s,%s,%s,%s,%s,%s\n", "source" , "target", "realValue", "layerID", "layerColor", "layerUnit" > "output/sankey/input2sankey.csv";

#------------------------------------------
# SANKEY - RESOURCES
#------------------------------------------
## Gasoline
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["CAR_GASOLINE", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Gasoline" , "Mob priv", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["CAR_GASOLINE","GASOLINE"] * F_t ["CAR_GASOLINE", h, td, r]  ) / 1000 , "Gasoline","#808080", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["CAR_PHEV", h, td, r] + F_t ["CAR_HEV", h, td, r] ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Gasoline" , "Mob priv", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["CAR_HEV","GASOLINE"] * F_t ["CAR_HEV", h, td, r] - layers_in_out["CAR_PHEV","GASOLINE"] * F_t ["CAR_PHEV", h, td, r]) / 1000 , "Gasoline","#808080", "TWh" >> "output/sankey/input2sankey.csv";
}

## Diesel
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["CAR_DIESEL", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Diesel" , "Mob priv", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["CAR_DIESEL","DIESEL"] * F_t ["CAR_DIESEL", h, td, r]  ) / 1000 , "Diesel", "#D3D3D3", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} ((F_t ["BUS_COACH_DIESEL", h, td, r] + F_t["BUS_COACH_HYDIESEL", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Diesel" , "Mob public", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["BUS_COACH_DIESEL","DIESEL"] * F_t ["BUS_COACH_DIESEL", h, td, r]   - layers_in_out["BUS_COACH_HYDIESEL","DIESEL"] * F_t ["BUS_COACH_HYDIESEL", h, td, r]   ) / 1000 , "Diesel", "#D3D3D3", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} ((F_t ["TRUCK", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Diesel" , "Freight", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["TRUCK","DIESEL"] * F_t ["TRUCK", h, td, r]  ) / 1000 , "Diesel", "#D3D3D3", "TWh" >> "output/sankey/input2sankey.csv";
}
#for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} ((F_t ["FARM_MACHINE", h, td, r])  ) > 0}{
#	printf "%s,%s,%.2f,%s,%s,%s\n", "Diesel" , "Farming", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["FARM_MACHINE","DIESEL"] * F_t ["FARM_MACHINE", h, td, r]  ) / 1000 , "Diesel", "#D3D3D3", "TWh" >> "output/sankey/input2sankey.csv";
#}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} ((F_t ["DEC_BOILER_OIL", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Diesel" , "Boilers", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["DEC_BOILER_OIL","DIESEL"] * F_t ["DEC_BOILER_OIL", h, td, r]  ) / 1000 , "Diesel", "#D3D3D3", "TWh" >> "output/sankey/input2sankey.csv";
}

## Natural Gas
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["CAR_NG", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "NG" , "Mob priv", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["CAR_NG","NG"] * F_t ["CAR_NG", h, td, r]  ) / 1000 , "NG", "#FFD700", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["BUS_COACH_CNG_STOICH", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "NG" , "Mob public", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["BUS_COACH_CNG_STOICH","NG"] * F_t ["BUS_COACH_CNG_STOICH", h, td, r]  ) / 1000 , "NG", "#FFD700", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["H2_NG", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "NG" , "H2 prod", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["H2_NG","NG"] * F_t ["H2_NG", h, td, r]  ) / 1000 , "NG", "#FFD700", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["CCGT", h, td, r] + F_t ["ICE_NG", h, td, r] ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "NG" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["CCGT","NG"] * F_t ["CCGT", h, td, r] -layers_in_out["ICE_NG","NG"] * F_t ["ICE_NG", h, td, r] ) / 1000 , "NG", "#FFD700", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["CCGT_CCS", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "NG CCS" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["CCGT_CCS","NG_CCS"] * F_t ["CCGT_CCS", h, td, r]  ) / 1000 , "NG", "#FFD700", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["IND_COGEN_GAS", h, td, r] + F_t ["DHN_COGEN_GAS", h, td, r] + F_t ["DEC_COGEN_GAS", h, td, r] + F_t ["DEC_ADVCOGEN_GAS", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "NG" , "CHP", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["IND_COGEN_GAS","NG"] * F_t ["IND_COGEN_GAS", h, td, r]   - layers_in_out["DHN_COGEN_GAS","NG"] * F_t ["DHN_COGEN_GAS", h, td, r]   - layers_in_out["DEC_COGEN_GAS","NG"] * F_t ["DEC_COGEN_GAS", h, td, r]   - layers_in_out["DEC_ADVCOGEN_GAS","NG"] * F_t ["DEC_ADVCOGEN_GAS", h, td, r]  ) / 1000 , "NG", "#FFD700", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["DEC_THHP_GAS", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "NG" , "HPs", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["DEC_THHP_GAS","NG"] * F_t ["DEC_THHP_GAS", h, td, r]  ) / 1000 , "NG", "#FFD700", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["IND_BOILER_GAS", h, td, r] + F_t ["DHN_BOILER_GAS", h, td, r] + F_t ["DEC_BOILER_GAS", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "NG" , "Boilers", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["IND_BOILER_GAS","NG"] * F_t ["IND_BOILER_GAS", h, td, r]   - layers_in_out["DHN_BOILER_GAS","NG"] * F_t ["DHN_BOILER_GAS", h, td, r]   - layers_in_out["DEC_BOILER_GAS","NG"] * F_t ["DEC_BOILER_GAS", h, td, r]  ) / 1000 , "NG", "#FFD700", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(( F_t ["DEC_THHP_GAS_COLD", h, td, r]) ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "NG" , "Refrig.", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["DEC_THHP_GAS_COLD","NG"] * F_t ["DEC_THHP_GAS_COLD", h, td, r]  ) / 1000 , "NG", "#FFD700", "TWh" >> "output/sankey/input2sankey.csv";
}

## Electricity production
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["ELECTRICITY", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Electricity" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["ELECTRICITY","ELECTRICITY"] * F_t ["ELECTRICITY", h, td, r]  ) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["NUCLEAR", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Nuclear" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["NUCLEAR","ELECTRICITY"] * F_t ["NUCLEAR", h, td, r]  ) / 1000 , "Nuclear", "#FFC0CB", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["WIND", h, td, r] + F_t ["WIND_OFF", h, td, r] ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Wind" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["WIND","ELECTRICITY"] * F_t ["WIND", h, td, r] + layers_in_out["WIND_OFF","ELECTRICITY"] * F_t ["WIND_OFF", h, td, r] ) / 1000 , "Wind", "#27AE34", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["HYDRO_DAM", h, td, r] + F_t ["NEW_HYDRO_DAM", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Hydro Dams" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["HYDRO_DAM","ELECTRICITY"] * F_t ["HYDRO_DAM", h, td, r] + layers_in_out["NEW_HYDRO_DAM","ELECTRICITY"] * F_t ["NEW_HYDRO_DAM", h, td, r] ) / 1000 , "Hydro Dam", "#00CED1", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["HYDRO_RIVER", h, td, r] + F_t ["NEW_HYDRO_RIVER", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Hydro River" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t],r in REGIONS}(layers_in_out["HYDRO_RIVER","ELECTRICITY"] * F_t ["HYDRO_RIVER", h, td, r] + layers_in_out["NEW_HYDRO_RIVER","ELECTRICITY"] * F_t ["NEW_HYDRO_RIVER", h, td, r]   ) / 1000 , "Hydro River", "#0000FF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["WAVE", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Wave" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t],r in REGIONS}(layers_in_out["WAVE","ELECTRICITY"] * F_t ["WAVE", h, td, r]) / 1000 , "Wave", "#0000II", "TWh" >> "output/sankey/input2sankey.csv";
}

# Coal
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["COAL_US", h, td, r] + F_t ["COAL_IGCC", h, td, r]) ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Coal" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["COAL_US","COAL"] * F_t ["COAL_US", h, td, r]   - layers_in_out["COAL_IGCC","COAL"] * F_t ["COAL_IGCC", h, td, r]  ) / 1000 , "Coal", "#A0522D", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["COAL_US_CCS", h, td, r] + F_t ["COAL_IGCC_CCS", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Coal CCS" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["COAL_US_CCS","COAL_CCS"] * F_t ["COAL_US_CCS", h, td, r]   - layers_in_out["COAL_IGCC_CCS","COAL"] * F_t ["COAL_IGCC_CCS", h, td, r]  ) / 1000 , "Coal", "#A0522D", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["IND_BOILER_COAL", h, td, r] + F_t ["DHN_BOILER_COAL", h, td, r]) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Coal" , "Boilers", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["IND_BOILER_COAL","COAL"] * F_t ["IND_BOILER_COAL", h, td, r] -layers_in_out["DHN_BOILER_COAL","COAL"] * F_t ["DHN_BOILER_COAL", h, td, r] ) / 1000 , "Coal", "#A0522D", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["IND_COGEN_COAL", h, td, r]) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Coal" , "CHP", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["IND_COGEN_COAL","COAL"] * F_t ["IND_COGEN_COAL", h, td, r] ) / 1000 , "Coal", "#A0522D", "TWh" >> "output/sankey/input2sankey.csv";
}


# Solar
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["PV", h, td, r] + F_t ["CSP", h, td, r] ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Solar" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["PV","ELECTRICITY"] * F_t ["PV", h, td, r] + layers_in_out["CSP","ELECTRICITY"] * F_t ["CSP", h, td, r] ) / 1000 , "Solar", "#FFFF00", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["DEC_SOLAR", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Solar" , "Heat LT Dec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}
		(layers_in_out["DEC_SOLAR","HEAT_LOW_T_DECEN"] * (F_t ["DEC_SOLAR", h, td, r])# SUPPRESSED # - Solar_excess [ h, td] ) 
		-((max(Storage_in["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_DIRECT_ELEC"  ,h,td,r]  /max(0.0001,Storage_in["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_HP_ELEC"      ,h,td,r]  /max(0.0001,Storage_in["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_THHP_GAS"     ,h,td,r]  /max(0.0001,Storage_in["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_BOILER_GAS"   ,h,td,r]  /max(0.0001,Storage_in["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_BOILER_WOOD"  ,h,td,r]  /max(0.0001,Storage_in["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_BOILER_OIL"   ,h,td,r]  /max(0.0001,Storage_in["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_COGEN_GAS"    ,h,td,r]  /max(0.0001,Storage_in["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_ADVCOGEN_GAS" ,h,td,r]  /max(0.0001,Storage_in["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_COGEN_OIL"    ,h,td,r]  /max(0.0001,Storage_in["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_ADVCOGEN_H2"  ,h,td,r]  /max(0.0001,Storage_in["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r] )))
		)/ 1000
		, "Solar", "#FFFF00", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["DEC_SOLAR", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Solar" , "Dec. Sto", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}
		((max(Storage_in["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_DIRECT_ELEC"  ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_HP_ELEC"      ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_THHP_GAS"     ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_BOILER_GAS"   ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_BOILER_WOOD"  ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_BOILER_OIL"   ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_COGEN_GAS"    ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_ADVCOGEN_GAS" ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_COGEN_OIL"    ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r],0))*(  F_t_Solar["DEC_ADVCOGEN_H2"  ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r] ))
		)/ 1000
		, "Solar", "#FFFF00", "TWh" >> "output/sankey/input2sankey.csv";
}


# Geothermal
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["GEOTHERMAL", h, td, r] + F_t ["GEOTHERMAL_ORC", h, td, r] ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Geothermal" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["GEOTHERMAL","ELECTRICITY"] * F_t ["GEOTHERMAL", h, td, r] +  layers_in_out["GEOTHERMAL_ORC","ELECTRICITY"] * F_t ["GEOTHERMAL_ORC", h, td, r]) / 1000 , "Geothermal", "#FF0000", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["DHN_DEEP_GEO", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Geothermal" , "DHN", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["DHN_DEEP_GEO","HEAT_LOW_T_DHN"] * F_t ["DHN_DEEP_GEO", h, td, r]  ) / 1000 , "Geothermal", "#FF0000", "TWh" >> "output/sankey/input2sankey.csv";
}

# Waste
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["IND_COGEN_WASTE", h, td, r] + F_t ["DHN_COGEN_WASTE", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Waste" , "CHP", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["IND_COGEN_WASTE","WASTE"] * F_t ["IND_COGEN_WASTE", h, td, r]  -layers_in_out["DHN_COGEN_WASTE","WASTE"] * F_t ["DHN_COGEN_WASTE", h, td, r]  ) / 1000 , "Waste", "#808000", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["IND_BOILER_WASTE", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Waste" , "Boilers", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["IND_BOILER_WASTE","WASTE"] * F_t ["IND_BOILER_WASTE", h, td, r]  ) / 1000 , "Waste", "#808000", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["WASTE_IN", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Waste" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["WASTE_IN","WASTE"] * F_t ["WASTE_IN", h, td, r]  ) / 1000 , "Waste", "#808000", "TWh" >> "output/sankey/input2sankey.csv";
}

# Oil
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["DEC_COGEN_OIL", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Oil" , "CHP", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["DEC_COGEN_OIL","LFO"] * F_t ["DEC_COGEN_OIL", h, td, r]  ) / 1000 , "Oil", "#8B008B", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["IND_BOILER_OIL", h, td, r] + F_t ["DHN_BOILER_OIL", h, td, r] )  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Oil" , "Boilers", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["IND_BOILER_OIL","LFO"] * F_t ["IND_BOILER_OIL", h, td, r] - layers_in_out["DHN_BOILER_OIL","LFO"] * F_t ["DHN_BOILER_OIL", h, td, r]  ) / 1000 , "Oil", "#8B008B", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["ICE_LFO", h, td, r] ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Oil" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["ICE_LFO","LFO"] * F_t ["ICE_LFO", h, td, r]) / 1000 , "Oil", "#8B008B", "TWh" >> "output/sankey/input2sankey.csv";
}

# Wood
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["H2_BIOMASS", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Wood" , "H2 prod", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["H2_BIOMASS","WOOD"] * F_t ["H2_BIOMASS", h, td, r]  ) / 1000 , "Wood", "#CD853F", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["GASIFICATION_SNG", h, td, r] + F_t ["PYROLYSIS", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Wood" , "Biofuels", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["GASIFICATION_SNG","WOOD"] * F_t ["GASIFICATION_SNG", h, td, r]   - layers_in_out["PYROLYSIS","WOOD"] * F_t ["PYROLYSIS", h, td, r]  ) / 1000 , "Wood", "#CD853F", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["IND_COGEN_WOOD", h, td, r] + F_t ["DHN_COGEN_WOOD", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Wood" , "CHP", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["IND_COGEN_WOOD","WOOD"] * F_t ["IND_COGEN_WOOD", h, td, r]   - layers_in_out["DHN_COGEN_WOOD","WOOD"] * F_t ["DHN_COGEN_WOOD", h, td, r]  ) / 1000 , "Wood", "#CD853F", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["IND_BOILER_WOOD", h, td, r] + F_t ["DHN_BOILER_WOOD", h, td, r] + F_t ["DEC_BOILER_WOOD", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Wood" , "Boilers", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["IND_BOILER_WOOD","WOOD"] * F_t ["IND_BOILER_WOOD", h, td, r]   - layers_in_out["DHN_BOILER_WOOD","WOOD"] * F_t ["DHN_BOILER_WOOD", h, td, r]   - layers_in_out["DEC_BOILER_WOOD","WOOD"] * F_t ["DEC_BOILER_WOOD", h, td, r]  ) / 1000 , "Wood", "#CD853F", "TWh" >> "output/sankey/input2sankey.csv";
}

#------------------------------------------
# SANKEY - Electricity use
#------------------------------------------
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["CAR_PHEV", h, td, r] + F_t ["CAR_BEV", h, td, r]) ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "Mob priv", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["CAR_PHEV","ELECTRICITY"] * F_t ["CAR_PHEV", h, td, r]   - layers_in_out["CAR_BEV","ELECTRICITY"] * F_t ["CAR_BEV", h, td, r]  ) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["TRAIN_PUB", h, td, r] + F_t ["TRAMWAY_TROLLEY", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "Mob public", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["TRAIN_PUB","ELECTRICITY"] * F_t ["TRAIN_PUB", h, td, r]   - layers_in_out["TRAMWAY_TROLLEY","ELECTRICITY"] * F_t ["TRAMWAY_TROLLEY", h, td, r]  ) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["TRAIN_FREIGHT", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "Freight", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["TRAIN_FREIGHT","ELECTRICITY"] * F_t ["TRAIN_FREIGHT", h, td, r]  ) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(Network_losses ["ELECTRICITY", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "Exp & Loss", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(Network_losses ["ELECTRICITY", h, td, r]   - layers_in_out["ELEC_EXPORT","ELECTRICITY"] * F_t ["ELEC_EXPORT", h, td, r]  ) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(End_Uses ["ELECTRICITY", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "Elec demand", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((End_Uses ["ELECTRICITY", h, td, r]  - Network_losses ["ELECTRICITY", h, td, r] - sum {i in STORAGE_OF_END_USES_TYPES["ELECTRICITY"]} (Storage_out [i, "ELECTRICITY", h, td, r]))  )/ 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
# New boxes for Electricity storage
for{{0}: sum{i in STORAGE_OF_END_USES_TYPES["ELECTRICITY"], t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(Storage_in [i, "ELECTRICITY", h, td, r]) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "Storage", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} (sum {i in STORAGE_OF_END_USES_TYPES["ELECTRICITY"] }(Storage_in [i, "ELECTRICITY", h, td, r]))/ 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{i in STORAGE_OF_END_USES_TYPES["ELECTRICITY"], t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(Storage_in [i, "ELECTRICITY", h, td, r]) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Storage" , "Elec demand", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(sum {i in STORAGE_OF_END_USES_TYPES["ELECTRICITY"] } (Storage_out [i, "ELECTRICITY", h, td, r])  )/ 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{i in STORAGE_OF_END_USES_TYPES["ELECTRICITY"], t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(Storage_in [i, "ELECTRICITY", h, td, r]) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Storage" , "Exp & Loss", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} (sum {i in STORAGE_OF_END_USES_TYPES["ELECTRICITY"] }((Storage_in [i, "ELECTRICITY", h, td, r])- (Storage_out [i, "ELECTRICITY", h, td, r] )  ))/ 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}

for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["DHN_HP_ELEC", h, td, r] + F_t ["DEC_HP_ELEC", h, td, r]) ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "HPs", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["DHN_HP_ELEC","ELECTRICITY"] * F_t ["DHN_HP_ELEC", h, td, r]   - layers_in_out["DEC_HP_ELEC","ELECTRICITY"] * F_t ["DEC_HP_ELEC", h, td, r]  ) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["IND_ELEC_COLD", h, td, r] + F_t ["DEC_ELEC_COLD", h, td, r]) ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "Refrig.", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["DEC_ELEC_COLD","ELECTRICITY"] * F_t ["DEC_ELEC_COLD", h, td, r]   - layers_in_out["IND_ELEC_COLD","ELECTRICITY"] * F_t ["IND_ELEC_COLD", h, td, r]  ) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["H2_ELECTROLYSIS", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "H2 prod", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["H2_ELECTROLYSIS","ELECTRICITY"] * F_t ["H2_ELECTROLYSIS", h, td, r]  ) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["DEC_DIRECT_ELEC", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "Heat LT Dec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["DEC_DIRECT_ELEC","HEAT_LOW_T_DECEN"] * F_t ["DEC_DIRECT_ELEC", h, td, r]  - ((max(Storage_in["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_DIRECT_ELEC"  ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r] )))) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS: Storage_in["TS_DEC_DIRECT_ELEC", "HEAT_LOW_T_DECEN", h, td, r] > Storage_out["TS_DEC_DIRECT_ELEC", "HEAT_LOW_T_DECEN", h, td, r] }    	((Storage_in["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td ,r])*(1-F_t_Solar["DEC_DIRECT_ELEC"  ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r] ))) >10 }{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "Dec. Sto", sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} 	((max(Storage_in["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_DIRECT_ELEC"  ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN", h, td, r] ))) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";	
}	
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["IND_DIRECT_ELEC", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "Heat HT", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["IND_DIRECT_ELEC","HEAT_HIGH_T"] * F_t ["IND_DIRECT_ELEC", h, td, r]  ) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["MOTOCYCLE", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "Mob priv", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["MOTOCYCLE","ELECTRICITY"] * F_t ["MOTOCYCLE", h, td, r]  ) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} ((F_t ["FARM_MACHINE", h, td, r])  ) > 0}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Elec" , "Farming", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["FARM_MACHINE","ELECTRICITY"] * F_t ["FARM_MACHINE", h, td, r]  ) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}


# H2 use
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["DEC_ADVCOGEN_H2", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "H2 prod" , "CHP", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["DEC_ADVCOGEN_H2","H2"] * F_t ["DEC_ADVCOGEN_H2", h, td, r]  ) / 1000 , "H2", "#FF00FF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["CAR_FUEL_CELL", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "H2 prod" , "Mob priv", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["CAR_FUEL_CELL","H2"] * F_t ["CAR_FUEL_CELL", h, td, r]  ) / 1000 , "H2", "#FF00FF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["BUS_COACH_FC_HYBRIDH2", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "H2 prod" , "Mob public", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["BUS_COACH_FC_HYBRIDH2","H2"] * F_t ["BUS_COACH_FC_HYBRIDH2", h, td, r]  ) / 1000 , "H2", "#FF00FF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}( F_t ["IND_BOILER_H2", h, td, r] ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "H2 prod" , "Boilers", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["IND_BOILER_H2","H2"] * F_t ["IND_BOILER_H2", h, td, r] ) / 1000 , "NG", "#FF00FF", "TWh" >> "output/sankey/input2sankey.csv";
}

#------------------------------------------
# SANKEY - HEATING
#------------------------------------------
# CHP
for{{0}: sum{i in COGEN, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t [ i, h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "CHP" , "Elec", sum{i in COGEN, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out[i,"ELECTRICITY"] * F_t [i, h, td, r]  ) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["DEC_COGEN_GAS", h, td, r] + F_t ["DEC_COGEN_OIL", h, td, r] + F_t ["DEC_ADVCOGEN_GAS", h, td, r] + F_t ["DEC_ADVCOGEN_H2", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "CHP" , "Heat LT Dec", sum{i in COGEN, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}
		(layers_in_out[i,"HEAT_LOW_T_DECEN"] * F_t [i, h, td, r])/1000 
		 -sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}
		 ((max(Storage_in["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_COGEN_GAS"    ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_ADVCOGEN_GAS" ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_COGEN_OIL"    ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r] ))+
		  (max(Storage_in["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_ADVCOGEN_H2"  ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r] ))
		  ) / 1000 , "Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} 
		    ((max(Storage_in["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_COGEN_GAS"    ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r] ))+
		     (max(Storage_in["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_ADVCOGEN_GAS" ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r] ))+
		     (max(Storage_in["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_COGEN_OIL"    ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r] ))+
		     (max(Storage_in["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_ADVCOGEN_H2"  ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r] )))> 10}{
		printf "%s,%s,%.2f,%s,%s,%s\n", "CHP" , "Dec. Sto", 
			sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}
				((max(Storage_in["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_COGEN_GAS"    ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_COGEN_GAS"   , "HEAT_LOW_T_DECEN", h, td, r] ))+
				(max(Storage_in["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_ADVCOGEN_GAS" ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_ADVCOGEN_GAS", "HEAT_LOW_T_DECEN", h, td, r] ))+
				(max(Storage_in["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_COGEN_OIL"    ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_COGEN_OIL"   , "HEAT_LOW_T_DECEN", h, td, r] ))+
				(max(Storage_in["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_ADVCOGEN_H2"  ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_ADVCOGEN_H2" , "HEAT_LOW_T_DECEN", h, td, r] ))) / 1000 , "Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}

for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["DHN_COGEN_GAS", h, td, r] + F_t ["DHN_COGEN_WOOD", h, td, r] + F_t ["DHN_COGEN_WASTE", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "CHP" , "DHN", sum{i in COGEN, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out[i,"HEAT_LOW_T_DHN"] * F_t [i, h, td, r]  ) / 1000 , "Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["IND_COGEN_GAS", h, td ,r] + F_t ["IND_COGEN_WOOD", h, td, r] + F_t ["IND_COGEN_WASTE", h, td, r] + F_t ["IND_COGEN_COAL", h, td, r] )  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "CHP" , "Heat HT", sum{i in COGEN, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out[i,"HEAT_HIGH_T"] * F_t [i, h, td, r]  ) / 1000 , "Heat HT", "#DC143C", "TWh" >> "output/sankey/input2sankey.csv";
}


# HPs
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["DEC_HP_ELEC", h, td, r] + F_t ["DEC_THHP_GAS", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "HPs" , "Heat LT Dec", 
		sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((layers_in_out["DEC_HP_ELEC","HEAT_LOW_T_DECEN"] * F_t ["DEC_HP_ELEC", h, td, r]   +	layers_in_out["DEC_THHP_GAS","HEAT_LOW_T_DECEN"] * F_t ["DEC_THHP_GAS", h, td, r]  
		-((max(Storage_in["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_HP_ELEC"      ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r] ))
     	 +(max(Storage_in["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_THHP_GAS"     ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r] )))
		) / 1000 ) , "Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["DHN_HP_ELEC", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "HPs" , "DHN", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((layers_in_out["DHN_HP_ELEC","HEAT_LOW_T_DHN"] * F_t ["DHN_HP_ELEC", h, td, r]  ) / 1000 ), "Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}

#storage
for{{0}: sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} 
    		((max(Storage_in["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_HP_ELEC"      ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r] ))+
     	    (max(Storage_in["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_THHP_GAS"     ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r] ))) >10 }{
		printf "%s,%s,%.2f,%s,%s,%s\n", "HPs" , "Dec. Sto", 		 
			sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} 
			((max(Storage_in["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_HP_ELEC"      ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_HP_ELEC"     , "HEAT_LOW_T_DECEN", h, td, r] ))+
			(max(Storage_in["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_THHP_GAS"     ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_THHP_GAS"    , "HEAT_LOW_T_DECEN", h, td, r] )))/1000
			,"Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";	
}

# Refrigeration
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["DEC_ELEC_COLD", h, td, r] + F_t ["DEC_THHP_GAS_COLD", h, td, r])  ) > 0}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Refrig." , "Cold Space", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["DEC_ELEC_COLD","COLD_SC"] * F_t ["DEC_ELEC_COLD", h, td, r] + layers_in_out["DEC_THHP_GAS_COLD","COLD_SC"] * F_t ["DEC_THHP_GAS_COLD", h, td, r] ) / 1000 , "Cold Space", "#DD1111", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["IND_ELEC_COLD", h, td, r])  ) > 0}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Refrig." , "Cold Process", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["IND_ELEC_COLD","COLD_PRO"] * F_t ["IND_ELEC_COLD", h, td, r]) / 1000 , "Cold Process", "#AA3131", "TWh" >> "output/sankey/input2sankey.csv";
}

# Biofuels
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["GASIFICATION_SNG", h, td, r] + F_t ["PYROLYSIS", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Biofuels" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["GASIFICATION_SNG","ELECTRICITY"] * F_t ["GASIFICATION_SNG", h, td, r]   + layers_in_out["PYROLYSIS","ELECTRICITY"] * F_t ["PYROLYSIS", h, td, r]  ) / 1000 , "Electricity", "#00BFFF", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["GASIFICATION_SNG", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Biofuels" , "NG", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["GASIFICATION_SNG","NG"] * F_t ["GASIFICATION_SNG", h, td, r]  ) / 1000 , "NG", "#FFD700", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["PYROLYSIS", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Biofuels" , "Oil", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["PYROLYSIS","LFO"] * F_t ["PYROLYSIS", h, td, r]  ) / 1000 , "Oil", "#8B008B", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["GASIFICATION_SNG", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Biofuels" , "DHN", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["GASIFICATION_SNG","HEAT_LOW_T_DHN"] * F_t ["GASIFICATION_SNG", h, td, r]  ) / 1000, "Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["BIODIESEL", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Biofuels" , "Diesel", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["BIODIESEL", h, td, r]   ) / 1000, "Diesel", "#AAAA88", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["BIOETHANOL", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Biofuels" , "Gasoline", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["BIOETHANOL", h, td, r]   ) / 1000, "Gasoline", "#808080", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["ICE_BIOLIQUID", h, td, r] +  F_t ["BIOMASS_ST", h, td, r]) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Biomass" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}( -layers_in_out["ICE_BIOLIQUID","BIOLIQUID"] * F_t ["ICE_BIOLIQUID", h, td, r] -layers_in_out["BIOMASS_ST","BIOLIQUID"] * F_t ["BIOMASS_ST", h, td, r] ) / 1000, "Electricity", "#GG0000", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["PSA", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Biomass" , "Bio-methane", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["PSA","BIOGAS"] * F_t ["PSA", h, td, r]  ) / 1000, "Biogas", "#GG0000", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["PSA", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Bio-methane", "NG", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out["PSA","NG"] * F_t ["PSA", h, td, r]  ) / 1000, "NG", "#FFD700", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["ICE_BIOGAS", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Biomass" , "Elec", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(-layers_in_out["ICE_BIOGAS","BIOGAS"] * F_t ["ICE_BIOGAS", h, td, r]  ) / 1000, "Electricity", "#GG0000", "TWh" >> "output/sankey/input2sankey.csv";
}

# Boilers
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(F_t ["DEC_BOILER_GAS", h, td, r] + F_t ["DEC_BOILER_WOOD", h, td, r] + F_t ["DEC_BOILER_OIL", h, td, r] ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Boilers" , "Heat LT Dec", sum{i in BOILERS, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} 
	(layers_in_out[i,"HEAT_LOW_T_DECEN"] * F_t [i, h, td, r] )/1000
	-sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}
		((max(Storage_in["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_BOILER_GAS"   ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r] ))+
		     (max(Storage_in["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_BOILER_WOOD"  ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r] ))+
		     (max(Storage_in["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_BOILER_OIL"   ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r] ))) / 1000 ,"Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} 
		    ((max(Storage_in["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_BOILER_GAS"   ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r] ))+
		     (max(Storage_in["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_BOILER_WOOD"  ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r] ))+
		     (max(Storage_in["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_BOILER_OIL"   ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r] ))) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Boilers" , "Dec. Sto", 
		sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} 
		    ((max(Storage_in["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_BOILER_GAS"   ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_BOILER_GAS"  , "HEAT_LOW_T_DECEN", h, td, r] ))+
		     (max(Storage_in["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_BOILER_WOOD"  ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_BOILER_WOOD" , "HEAT_LOW_T_DECEN", h, td, r] ))+
		     (max(Storage_in["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r] - Storage_out["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r],0))*(1-F_t_Solar["DEC_BOILER_OIL"   ,h,td, r]  /max(0.0001,Storage_in["TS_DEC_BOILER_OIL"  , "HEAT_LOW_T_DECEN", h, td, r] ))		 ) / 1000 ,"Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}

for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["DHN_BOILER_GAS", h, td, r] + F_t ["DHN_BOILER_WOOD", h, td, r] + F_t ["DHN_BOILER_OIL", h, td, r] + F_t ["DHN_BOILER_COAL", h, td, r])  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Boilers" , "DHN", sum{i in BOILERS, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out[i,"HEAT_LOW_T_DHN"] * F_t [i, h, td, r]  ) / 1000 , "Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}((F_t ["IND_BOILER_GAS", h, td, r] + F_t ["IND_BOILER_WOOD", h, td, r] + F_t ["IND_BOILER_OIL", h, td, r] + F_t ["IND_BOILER_COAL", h, td, r] + F_t ["IND_BOILER_WASTE", h, td, r] + F_t ["IND_BOILER_H2", h, td, r])  ) > 10 }{
	printf "%s,%s,%.2f,%s,%s,%s\n", "Boilers" , "Heat HT", sum{i in BOILERS, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(layers_in_out[i,"HEAT_HIGH_T"] * F_t [i, h, td, r]  ) / 1000 , "Heat HT", "#DC143C", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], i in STORAGE_OF_END_USES_TYPES["HEAT_LOW_T_DECEN"], r in REGIONS: Storage_in[i, "HEAT_LOW_T_DECEN", h, td, r] < Storage_out[i, "HEAT_LOW_T_DECEN", h, td, r] } (Storage_out[i , "HEAT_LOW_T_DECEN", h, td, r] - Storage_in[i , "HEAT_LOW_T_DECEN", h, td, r]) > 10}{
   printf "%s,%s,%.2f,%s,%s,%s\n", "Dec. Sto" , "Heat LT Dec", sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], i in STORAGE_OF_END_USES_TYPES["HEAT_LOW_T_DECEN"], r in REGIONS: Storage_in[i, "HEAT_LOW_T_DECEN", h, td, r] < Storage_out[i, "HEAT_LOW_T_DECEN", h, td, r] } (Storage_out[i , "HEAT_LOW_T_DECEN", h, td, r] - Storage_in[i , "HEAT_LOW_T_DECEN", h, td, r])/1000 , "Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}

# DHN 
for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(End_Uses ["HEAT_LOW_T_DHN", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "DHN" , "Heat LT DHN", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} (sum {i in TECHNOLOGIES diff STORAGE_TECH } (layers_in_out[i, "HEAT_LOW_T_DHN"] * F_t [i, h, td, r]  ) 	- Network_losses ["HEAT_LOW_T_DHN", h, td, r]   	- sum {i in STORAGE_OF_END_USES_TYPES["HEAT_LOW_T_DHN"]} (Storage_in  [i, "HEAT_LOW_T_DHN", h, td, r])) / 1000	, "Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}

for{{0}: sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(Network_losses ["HEAT_LOW_T_DHN", h, td, r]  ) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "DHN" , "Loss DHN", sum{t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(Network_losses ["HEAT_LOW_T_DHN", h, td, r]  ) / 1000 , "Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}
# DHN storage :
for{{0}: sum {i in STORAGE_OF_END_USES_TYPES["HEAT_LOW_T_DHN"],t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(Storage_in  [i, "HEAT_LOW_T_DHN", h, td, r]) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "DHN" , "DHN Sto", sum {i in STORAGE_OF_END_USES_TYPES["HEAT_LOW_T_DHN"],t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} (Storage_in  [i, "HEAT_LOW_T_DHN", h, td, r])/1000	, "Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}
for{{0}: sum {i in STORAGE_OF_END_USES_TYPES["HEAT_LOW_T_DHN"],t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS}(Storage_out  [i, "HEAT_LOW_T_DHN", h, td, r]) > 10}{
	printf "%s,%s,%.2f,%s,%s,%s\n", "DHN Sto" , "Heat LT DHN", sum {i in STORAGE_OF_END_USES_TYPES["HEAT_LOW_T_DHN"],t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t], r in REGIONS} (Storage_out  [i, "HEAT_LOW_T_DHN", h, td, r])/1000	, "Heat LT", "#FA8072", "TWh" >> "output/sankey/input2sankey.csv";
}