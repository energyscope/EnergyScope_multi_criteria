Releases
++++++++

How to cite
===========

In the academic spirit of collaboration, the source code should be appropriately acknowledged in the resulting scientific disseminations.
You may cite it as follows:

* [1], for general reference to the EnergyScope project and the EnergyScope modeling framework :cite:`Limpens2019`
* [2], for reference to the origins of the EnergyScope project or to the first online version of the calculator energyscope.ch :cite:`Girones2015`
* [3], for reference to the energyscope MILP modeling framework :cite:`Moret2016`
* [4], for reference to the current code :cite:`Limpens2021thesis`


[1] G. Limpens, S . Moret, H. Jeanmart, F. Maréchal (2019). EnergyScope TD: a novel open-source model for regional energy systems and its application to the case of Switzerland. https://doi.org/10.1016/j.apenergy.2019.113729	

[2] V. Codina Gironès, S. Moret, F. Maréchal, D. Favrat (2015). Strategic energy planning for large-scale energy systems: A modelling framework to aid decision-making. Energy, 90(PA1), 173–186. https://doi.org/10.1016/j.energy.2015.06.008   	

[3] S. Moret, M. Bierlaire, F. Maréchal (2016). Strategic Energy Planning under Uncertainty: a Mixed-Integer Linear Programming Modeling Framework for Large-Scale Energy Systems. https://doi.org/10.1016/B978-0-444-63428-3.50321-0  	

[4] G. Limpens (2021). Generating energy transition pathways: application to Belgium. PhD thesis Université Catholique de Louvain. http://hdl.handle.net/2078.1/249196


You are welcome to report any bugs related to the code to the following:
moret.stefano@gmail.com or gauthierLimpens@gmail.com

Or by submitting an issue on the github repository.

License
=======

Copyright (C) <2018-2021> <Ecole Polytechnique Fédérale de Lausanne (EPFL), Switzerland and Université catholique de Louvain (UCLouvain), Belgium>

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License

Codes versions
==============
- first release (v1, monthly MILP) of the EnergyScope (ES) model: https://github.com/energyscope/EnergyScope/tree/v1.0 . See :cite:t:`Moret2017PhDThesis`.
- second release (v2, hourly LP) of the EnergyScope (ES) model: https://github.com/energyscope/EnergyScope/tree/v2.0 .	See :cite:t:`Limpens2019`.
- second release with energy system improvment (v2.1 Energy system update) of EnergyScope (ES) model: https://github.com/energyscope/EnergyScope/tree/v2.1 . See :cite:t:`Limpens_belgian_2020`.

Authors: 

- Stefano Moret, Ecole Polytechnique Fédérale de Lausanne (Switzerland), <moret.stefano@gmail.com> 
- Gauthier Limpens, Université catholique de Louvain (Belgium), <gauthierLimpens@gmail.com>  
- Paolo Thiran, Université catholique de Louvain (Belgium)
- Xavier Rixhon, Université catholique de Louvain (Belgium)


Model extensions
================

The EnergyScope TD models account for two published model extension:

- Pathway optimisation: *EnergyScope Pathway* enables to optimise the energy system from an existing year (usually 2015) 
  to a future target year. The model has been extended to a big linear model which represents 8 representative years from 2015 to 2050. 
  The overall transition is optimised at once with a perfect foresight on technology performances (prices, efficiency,...), resources prices, energy demand ...
  
  **Main contributors**: Gauthier Limpens, see :cite:`Limpens2021thesis`

- Multi-region; *EnergyScope Multi-Cells* allows the representation of several region at once. 
  The regions are resolved simultaneously with the exchanges of several energy carriers (usually electricity, molecules and wood).
  The new model has been first developped by :cite:t:`thiranenergyscope` on a fictive case, then extended to the Europe region with a 6-cells resolution, see :cite:t:`cornet2021energy`.
  
  **Main contributors**: Paolo Thiran, see :cite:`thiranenergyscope,cornet2021energy,thiran2021flexibility`

Applications
============

The model has been used for:

- *Uncertainty quantification*:
  
    * *Robust optimisation design*: Moret developed a framework to integrate uncertainties in energy models. The framework accounts for uncertainty characterisation, sensitivity analysis and robust optimisation.
  
    **Main contributors**: Stefano Moret, see :cite:`Moret2017PhDThesis`.
    
    * *Global sensitivity analysis (GSA)*: this allow to identify the critical parameters for the energy transition. As an example, :cite:t:`Moret2017PhDThesis`
    quantifies how the price of fossil ressources drive the uncertainty. This result was verified for the case of Belgium and compared to other decision, such as phasing out Nuclear (see studies of :cite:t:`Limpens2021thesis` and :cite:t:`rixhon2021role`).
    
    **Main contributors**: Gauthier Limpens, Xavier Rixhon and Diederik Coppiters, see :cite:`Moret2017PhDThesis,Limpens2021thesis,rixhon2021role,limpens2020impact`.

- *Scenario analysis of the transition*: the model has been applied to study different scenarios of transition for the Swiss (see :cite:`Limpens2019,Limpens_role_2019`) and the Belgian case (see :cite:`Limpens_belgian_2020,Limpens2021thesis`).
  The analysis enable to quantify the role of storage technologies (i.e. electricity, heat and molecule storage), 
  identify the key technologies of the transition or even estimate the cost for each transition option.
  
  **Main contributors**: Gauthier Limpens and Stefano Moret, see :cite:`Limpens2019,Limpens_role_2019,Limpens_belgian_2020,Limpens2021thesis`.


Case studies
============

The model has been applied to the following countries:

- Switzerland:
  
    * *Uncertainty*: :cite:t:`Moret2017PhDThesis`
    * *Scenario analysis and storage needs*: see for the main study :cite:t:`Limpens2019` and :cite:t:`Limpens_role_2019` for a specific study on the storage.
  
- Belgium:
  
    * *Scenarios analysis*: see :cite:t:`Limpens_belgian_2020` who analysed different scenarios to reduce greenhouse gases emissions.
    * *Uncertainty*: see :cite:t:`limpens2020impact` for the elaboration of the methodology to the Belgium case (using a novel methodology), see :cite:t:`rixhon2021role` for a specific study on electro-fuels and see :cite:t:`Limpens2021thesis` for an updated study on the Belgian case.
  
- Italy:
  
    * *Scenarios analysis*: see :cite:t:`borasio2022deep` for an exhaustive analysis (per regions and with uncertainty) to reduce the energy system at the horizon of 2050.
    * *Multi-region analysis*: see :cite:t:`thiran2021flexibility` for an application of the Multi-cell model to a three region case.

- Spain:
  
    * *Scenario analysis*: see :cite:t:`rosello2021study` for different scenarios of transition in Spain.

- Other countries:
  
    * *European Union countries* see :cite:t:`dommissemodelling` for a data collection and results for 26 european countries.
  
Current developments:
=====================

- Pathway: Myopic optimisation
  
- Multi-cells: work on the selection of typical days and application to a larger region.
  
- Multi-criteria: Use of additional criteria (Global warming potential, energy embodied, ...), see :cite:t:`muyldermans2021multicriteria`

- Coupling with other models: undergoing works try to couple the EnergyScope model with a dispatch model, see :cite:t:`coates2020energy`

- (And also works from Stefano and EPFL)
