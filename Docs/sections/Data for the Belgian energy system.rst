Data for the Belgian energy system
++++++++++++++++++++++++++++++++++

.. caution ::
   This section is still under construction.
   It is built from Limpens PhD thesis (2021) available at http://dx.doi.org/10.13140/RG.2.2.25755.18724 


.. role:: raw-latex(raw)
   :format: latex
..

.. _app:bestd_data:

Belgian energy system data in 2035
==================================

Overview This appendix reports the input data for the application of the
LP modeling framework to the case study of Belgium between 2015 and
2050. Data are detailed for the year 2035 and 2015, the latter used for
model verification. Trends to extrapolated these data for the other
years are given. This appendix is an improved version previously
presented in :raw-latex:`\citep{Limpens2019,Limpens_belgian_2020}`

The data can be grouped into three parts: resources, demand and
technologies. For resources, the work of the JRC
:raw-latex:`\cite{simoes2013jrc}`, Biomass atlas
:raw-latex:`\cite{elbersen2012atlas}` and
:raw-latex:`\citet{brynolf2018electrofuels}` have been used to
complement and confirm the prices already reported in previous works
:raw-latex:`\citep{Moret2017PhDThesis,Limpens2019,limpens2020impact}`.
For energy demand, the annual demand is calculated from the work of the
European Commission’s projections up to 2050
:raw-latex:`\cite{EuropeanCommission2016}`. As a complement, the time
series are all calculated on the basis of the year 2015. For
technologies, they are characterised by the following characteristics:
energy balances, cost (investment and maintenance), and environmental
impact (global warming potential (GWP)). For weather dependent technologies (wind, solar, etc.), real
production for the year 2015 was collected from the TSO.

For GWP and GHG emissions, LCA data are taken from the Ecoinvent
database v3.2 [1]_ :raw-latex:`\cite{weidema_ecoinvent_2013}` using the
“allocation at the point of substitution” method. GWP is assessed with
the “GWP100a - IPCC2013” indicator. For technologies, the GWP impact
accounts for the technology construction; for resources, it accounts for
extraction, transportation and combustion. In addition, data for fuel
combustion are taken from :raw-latex:`\citet{Quaschning2015}`.

For the cost, the reported data are the nominal values for Belgium in
the year 2035 All costs are expressed in *real*\  [2]_ Euros for the
year 2015 (€\ :sub:`2015`). If not specified, € refers to
€\ :sub:`2015`. All cost data used in the model originally expressed in
other currencies or referring to another year are converted to
€\ :sub:`2015` to offer a coherent comparison. Most of the data come
from a previous work :raw-latex:`\cite{Moret2017PhDThesis,Limpens2019}`,
and were expressed in CHF\ :sub:`2015` (Based on the average annual
exchange rate value from ECB https://www.ecb.europa.eu, the annual rate
was 1€\ :sub:`2015` = 1.0679CHF\ :sub:`2015`). The method used for the
year conversion is illustrated by Eq. :eq:`eqn:currency_conv`.

.. math::
    c_{inv} [\text{€}_{2015}] = c_{inv} [C_y] \cdot  \frac{\text{USD}_y}{C_y}  \cdot \frac{\text{CEPCI}_{2015} \ [\text{USD}_{2015}]}{\text{CEPCI}_y \ [\text{USD}_y]} \cdot \frac{\text{€}_{2015}}{\text{USD}_{2015}} 
    :label: eqn:currency_conv

Where :math:`C` and :math:`y` are the currency and the year in which the
original cost data are expressed, respectively, USD is the symbol of
American Dollars and the CEPCI
:raw-latex:`\cite{chemical_engineering_chemical_2016}` is an index
taking into account the evolution of the equipment cost (values reported
in Table `1.1 <#tbl:cepci>`__). As an example, if the cost data are
originally in EUR\ :sub:`2010`, they are first converted to
USD\ :sub:`2010`, then brought to USD\ :sub:`2015` taking into account
the evolution of the equipment cost (by using the CEPCI), and finally
converted to €\ :sub:`2015`. The intermediate conversion to USD is
motivated by the fact that the CEPCI is expressed in *nominal* USD.
Although this conversion method is originally defined for
technology-related costs, in this paper as a simplification it used also
for the cost of resources.


.. container::
   :name: tbl:cepci

   .. table:: CEPCI values :raw-latex:`\cite{chemical_engineering_chemical_2016}`

      ======== =========
      **Year** **CEPCI**
      ======== =========
      1982     285.8
      1990     357.6
      1991     362.3
      1992     367.0
      1993     371.7
      1994     376.4
      1995     381.1
      1996     381.7
      1997     386.5
      1998     389.5
      1999     390.6
      2000     394.1
      2001     394.3
      2002     395.6
      2003     402.0
      2004     444.2
      2005     468.2
      2006     499.6
      2007     525.4
      2008     575.4
      2009     521.9
      2010     550.8
      2011     585.7
      2012     584.6
      2013     567.3
      2014     576.1
      2015     556.3
      ======== =========


The current appendix is built in three parts. At first, data are given
for the year 2035 for resources (Section
`1.1 <#app:sec:BESTD_resources>`__), demand (Section
`1.2 <#sec:app1_end_uses>`__) and technologies (Section
`1.3 <#app:BESTD_data_technologies>`__. Then, the year 2015 is discussed
as real data have been collected for this case. And finally, the
extension of the data from year 2035 to other years are detailed.

.. _app:sec:BESTD_resources:

Resources
---------

The availability of all resources, except for biomass, and non-RE waste,
is set to a value high enough to allow unlimited use in the model. Table
`[tbl:prices_resources] <#tbl:prices_resources>`__ details the prices of
resources (:math:`c_{op}`), the GHG emissions (:math:`gwp_{op}`) associated to their
production, transportation and combustion; and endogenous availability
of resources. Export of electricity are possible, but they are
associated to a zero selling price. Two kinds of emissions are proposed:
one accounting for the impact associated to production, transport and
combustion (based on GWP100a -
IPCC2013 :raw-latex:`\cite{Moret2017PhDThesis}`); the other accounting
only for combustion (based on :raw-latex:`\citet{Quaschning2015}`).
Total emissions are used to assess energy system emissions. Combustion
only is used to calculate the direct CO2 emissions that can be captured
and used through a carbon capture technology (latter presented).

Local renewable resources
~~~~~~~~~~~~~~~~~~~~~~~~~

The majors renewable potentials are: solar, biomass and wind.
Additionnaly, Belgium has hydro and perhaps affordable geothermal. Wind,
solar, hydro and geothermal are limited by the number of technologies
deployable, while biomass is limited by the amount of resources
available.

Wind, solar, hydro and geothermal
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The estimation of these resources have been done in Chapter
`[ch:case_study] <#ch:case_study>`__ (see Section
`[ssec:be_re_potential] <#ssec:be_re_potential>`__).


Biomass and non-RE waste
^^^^^^^^^^^^^^^^^^^^^^^^

In an European study, :raw-latex:`\citet{elbersen2012atlas}` drew the
biomass atlas of EU countries for different scenarios in terms of prices
and potentials. According to a conservative approach, the sustainable
scenario estimations are selected. In their work, biomass is declined in
a larger variety of form. To adapt these data to our work, these
varieties are aggregated into three types: woody biomass, wet biomass
and non-RE waste. Waste accounts for common sludges, MSW landfill, MSW
not landfill (composting, recycling) and paper cardboard. The overall
potential is estimated to 17.8 TWh/y with an approximate price of
10.0 €/MWh. The price is estimated as a weighted sum between the
different variety and their specific price (given in the document). Wet
biomass accounts for all the digestible biomass, which are verge gras,
perennials (grassy), prunings, total manure, grass cuttings abandoned
grassland, animal waste and forrage maize (biogas). The overall
potential is estimated to 38.9 TWh/y with an approximate price of
2.5 €/MWh. Woody biomass accounts for all the non-digestible biomass,
which are roundwood (including additional harvestable roundwood), black
liquor, landscape care wood, other industrial wood residues, perennials
(woody), post consumer wood, saw-dust, sawmill by-products (excluding
sawdust) and primary forestry residues. The overall potential is
estimated to 23.4 TWh/y with an approximate price of 14.3 €/MWh.

Oleaginous (0.395 TWh/y) and sugary (0 TWh/y) potentials are two order
of magnitude below the previous categories and thus neglected.

However, these costs do not account for treatment and transportation.
Based on a local expert (from Coopeos), a MWh of wood ready to use for
small wood boilers is negotiated around 28 €/MWh today, twice much than
estimated prices. This order of magnitude is in line with the Joint
Research Center price estimation in 2030
:raw-latex:`\cite{simoes2013jrc}`. Thus, the price proposed in
:raw-latex:`\cite{elbersen2012atlas}` are doubled. It results in prices
for woody biomass, wet biomass and waste of 28.5, 5.0 and 20.0  €/MWh in
2015, respectively. The price for biomass is expected to increase by
27.7% up to 2050 :raw-latex:`\cite{simoes2013jrc}`. By adapting these
value to 2035, the prices are for 32.8 €/MWh woody biomass, 5.8 €/MWh
for wet biomass and for 23.1 €/MWh for waste.

Imported resources
~~~~~~~~~~~~~~~~~~

Dominating fossil fuels are implemented in the model and detailed in
Section
`[ssec:case_study_imported_res] <#ssec:case_study_imported_res>`__. They
can be regrouped in hydrocabons (gasoline, diesel, LFO and NG), coal and
uranium. Data is summarised in Table
`[tbl:prices_resources] <#tbl:prices_resources>`__ and are compared to
other sources, such as estimations from the JRC of prices for oil, gas
and coal :raw-latex:`\cite{simoes2013jrc}`. They base their work on a
communication of the European Commission
:raw-latex:`\cite{eu2011roadmap}`.

Fuel can also be produced from renewable feedstocks: biomass or
renewable electricity. :raw-latex:`\citet{brynolf2018electrofuels}`
estimates a range for the production cost for some electro-fuels based
on hydrogen electrolysis: methane, methanol, DME, gasoline and diesel.
Hereafter, we will assume that the price of an electro-fuel is equal to
its production cost. In addition, imported bio-fuels are assumed to have
the same price as their equivalent electro-fuel. Finally, the costs are
estimated in 2015 and 2030 in
:raw-latex:`\cite{brynolf2018electrofuels}`. As no estimates are made
thereafter, the 2030 value is imposed in 2050 and a linear improvement
is assumed between 2015 and 2050 [3]_.


.. container::
   :name: foot:electrofuels_noCO2emissions

   .. table:: Price, GHG emissions and availability of resources, in 2035. Abbreviations: LFO, NG, SLF and SNG.

      +-------------+-------------+-------------+-------------+-------------+
      | **          | :math:`c_   | :math:`gwp_ | :math:`{CO}_| *avail*     |
      | Resources** | {op}`       | {op}`       | {2direct}`  |             |
      |             |             |             | [26]_       |             |
      +-------------+-------------+-------------+-------------+-------------+
      |             |             | [€\ :sub:`2 | [kgC        | [kgCO\ :sub |
      |             |             | 015`/MWh\   | O\ :sub:`2` | :`2`/MWh\ : |
      |             |             | :sub:`fuel`]| -eq./MWh\ : | sub:`fuel`] |
      |             |             |             | sub:`fuel`] |             |
      +-------------+-------------+-------------+-------------+-------------+
      | Electricity | 84.3 [27]_  | 275.3 [28]_ | 0           | 27.5        |
      | Import      |             |             |             |             |
      +-------------+-------------+-------------+-------------+-------------+
      | Gasoline    | 82.4 [29]_  | 345         | 250         | infinity    |
      |             |             |             |             |             |
      +-------------+-------------+-------------+-------------+-------------+
      | Diesel      | 79.7 [30]_  | 315         | 270         | infinity    |
      |             |             |             |             |             |
      +-------------+-------------+-------------+-------------+-------------+
      | LFO         | 60.1 [31]_  | 311.5       | 260         | infinity    |
      |             |             |             |             |             |
      +-------------+-------------+-------------+-------------+-------------+
      | NG          | 44.3 [32]_  | 267         | 200         | infinity    |
      |             |             |             |             |             |
      +-------------+-------------+-------------+-------------+-------------+
      | Woody       | 32.8        | 11.8        | 390         | 23.4        |
      | biomass     |             |             |             |             |
      +-------------+-------------+-------------+-------------+-------------+
      | Wet-biomass | 5.8         | 11.8        | 390         | 38.9        |
      +-------------+-------------+-------------+-------------+-------------+
      | non-RE      | 23.1        | 150         | 260 [33]_   | 17.8        |
      | waste       |             |             |             |             |
      +-------------+-------------+-------------+-------------+-------------+
      | Coal        | 17.6        | 401         | 360         | infinity    |
      |             |             | :raw-late   |             |             |
      |             |             | x:`\cite{we |             |             |
      |             |             | idema_ecoin |             |             |
      |             |             | vent_2013}` |             |             |
      +-------------+-------------+-------------+-------------+-------------+
      | Uranium     | 3.9 [34]_   | 3.9         | 0           | infinity    |
      |             |             | :raw-late   |             |             |
      |             |             | x:`\cite{we |             |             |
      |             |             | idema_ecoin |             |             |
      |             |             | vent_2013}` |             |             |
      +-------------+-------------+-------------+-------------+-------------+
      | Bio-diesel  | 240.0 [35]_ | 0  [36]_    | 270         | infinity    |
      |             |             |             |             |             |
      +-------------+-------------+-------------+-------------+-------------+
      | B           | 225.7       | 0           | 250         | infinity    |
      | io-gasoline |             |             |             |             |
      +-------------+-------------+-------------+-------------+-------------+
      | SLF         | 211.4       | 0           | 260         | infinity    |
      |             |             |             |             |             |
      +-------------+-------------+-------------+-------------+-------------+
      | SNG         | 197.1       | 0           | 200         | infinity    |
      |             |             |             |             |             |
      +-------------+-------------+-------------+-------------+-------------+
      | H2          | 177.1       | 0           | 0           | infinity    |
      |             |             |             |             |             |
      +-------------+-------------+-------------+-------------+-------------+


.. _sec:app1_end_uses:

Energy demand and political framework
-------------------------------------

The EUD for heating, electricity and mobility in 2035 is calculated from
the forecast done by the EUC in 2035 for Belgium (see Appendix 2 in
:raw-latex:`\cite{EuropeanCommission2016}`). However, in
:raw-latex:`\cite{EuropeanCommission2016}`, the FEC is given for heating
and electricity. The difference between FEC and EUD is detailed in
Section
`[ssec:conceptual_modelling_framework] <#ssec:conceptual_modelling_framework>`__
and can be summarised as follows: the FEC is the amount of input energy
needed to satisfy the EUD in energy services. Except for HP, the FEC is
greater than EUD. We applied a conservative approach by assuming that
the EUD equal to the FEC for electricity and heating demand.

.. _ssec:app1_electricity_end_uses:

Electricity
~~~~~~~~~~~

The values in table `1.3 <#tbl:elec_demand>`__ list the electricity
demand that is not related to heating for the three sectors in 2035. The
overall electricity EUD is given in
:raw-latex:`\cite{EuropeanCommission2016}`. However, only the FEC is
given by sectors. In order to compute the share of electricity by
sector, we assume that the electricity to heat ratio for the residential
and services remain constant between 2015 and 2035. This ratio can be
calculated from :raw-latex:`\citet{EuropeanCommission-Eurostat.2018}`,
these ratio of electricity consumed are 24.9% and 58.2% for residential
and services, respectively. As a consequence, the industrial electricity
demand is equal to the difference between the overall electricity demand
and the two other sectors.

A part of the electricity is assumed to be a fixed demand, such as
fridges in households and services, or industrial processes. The other
part is varying, such as the lighting demand. The ratio between varying
electricity and fixed demand are the one of Switzerland, presented in
:raw-latex:`\cite{Limpens2019,Moret2017PhDThesis}` which are based on
:raw-latex:`\cite{prognos_ag_energieperspektiven_2012}`. The varying
demand of electricity is shared over the year according to *%\ elec*,
which is represented in Figure `1.1 <#fig:TS_elec>`__. We use the real
2015 Belgian electricity demand (data provided by ENTSO-E
https://www.entsoe.eu/). *%\ elec* time series is the normalised value
of the difference between the real time series and its minimum value.

.. container::
   :name: tbl:elec_demand

   .. table:: Yearly electricity demand not related to heating by sector, in 2035.

      ========== =========== ============
      \          **Varying** **Constant**
      \          [TWh]       [TWh]
      Households 0.8         21.9
      Industry   4.8         40.0
      Services   5.1         20.1
      ========== =========== ============

.. figure:: /images/belgian_data/ts_elec_Belgium.png
   :alt: Normalised electricity time series over the year.
   :name: fig:TS_elec

   Normalised electricity time series over the year.


.. _ssec:app1_heating_end_uses:

Heating
~~~~~~~

We applied the same methodology as in previous paragraph to compute the
residential, service heat yearly demand. The industrial heat processes
demand is assumed to be the overall industrial energy demand where
electricity and non energy use have been removed. Yearly EUD per sector
is reported in table `1.4 <#tbl:heat_demand>`__.

A part of the heat is assumed to be a fixed demand, such as hot water in
households and services, or industrial processes. The other part
represents the space heating demand and is varying. Similarly to the
electricity, the ratio between varying electricity and fixed demand are
the one of Switzerland, presented in
:raw-latex:`\cite{Limpens2019,Moret2017PhDThesis}` which are based on
:raw-latex:`\cite{prognos_ag_energieperspektiven_2012}`. The varying
demand of heat is shared over the year according to :math:`%_{sh}`. This time
series is based on our own calculation. The methodology is the
following: based on the temperature time series of Uccle 2015 (data from
IRM :raw-latex:`\cite{Reyniers2012}`); the HDH are calculated; and then
the time series. The HDH is a similar approach than the more commonly
used HDD. According to Wikipedia, HDD is defined as follows: “*HDD is a
measurement designed to quantify the demand for energy needed to heat a
building. HDD is derived from measurements of outside air temperature.
The heating requirements for a given building at a specific location are
considered to be directly proportional to the number of HDD at that
location. [...] Heating degree days are defined relative to a base
temperature*”. According to the European Environment Agency [37]_, the
base temperature is 15.5\ :math:`^o`\ C, we took 16\ :math:`^o`\ C. HDH
are computed as the difference between ambient temperature and the
reference temperature at each hour of the year. If the ambient
temperature is above the reference temperature, no heating is needed.
Figure `1.2 <#fig:HDD_BE_2015>`__ compares the result of our methodology
with real value collected by Eurostat [38]_. The annual HDD was 2633,
where we find 2507.

By normalising the HDH, we find :math:`%_{sh}`, which is represented in Figure
`1.3 <#fig:TS_heat>`__.

.. figure:: /images/belgian_data/belgium_HDD_2015.png
   :alt: Comparison of HDD between Eurostat and our own calculation.
   :name: fig:HDD_BE_2015

   Comparison of HDD between Eurostat and our own calculation.

.. figure:: /images/belgian_data/ts_sh_Belgium.png
   :alt: Normalised space heating time series over the year.
   :name: fig:TS_heat

   Normalised space heating time series over the year.

.. container::
   :name: tbl:heat_demand

   .. table:: Yearly heat end use demand per sector, in 2035.

      ========== ================= ============= ========================
      \          **Space heating** **Hot water** **Process heat**\  [39]_
      \          [TWh]             [TWh]         [TWh]
      Households 65.9              16.8          0
      Industry   17.0              5.2           65.3
      Services   23.1              4.4           0
      ========== ================= ============= ========================
.. [39]
   We define process heat as the high temperature heat required in the
   industrial processes. This heat cannot be supplied by technologies
   such as heat pumps or thermal solar.

.. _ssec:app1_demand_mobility:

Mobility
~~~~~~~~

The annual passenger transport demand in Belgium for 2035 is expected
to be 194 billions :raw-latex:`\cite{EuropeanCommission2016}`.
Passenger transport demand is divided between public and private
transport. The lower (:math:`%_{public,min}`) and upper bounds
(:math:`%_{public,max}`) for the use of public transport are 19.9% [40]_ and
50% of the annual passenger transport demand, respectively. The
passenger mobility demand is shared over the day according to
:math:`%_{pass}`. We assume a constant passenger mobility demand for every
day of the year. This latter is represented in Figure
`1.4 <#fig:TS_mobPass>`__ (data from Figure 12 of
:raw-latex:`\cite{USTransportation}`).
The annual freight transport demand in Belgium for 2035 is expected to
be 98e09 tons kilometers :raw-latex:`\cite{EuropeanCommission2016}`.
The freight can be supplied by trucks, trains or boats. The lower
(:math:`%_{fr,rail,min}`) and upper bounds (:math:`%_{fr,rail,max}`) for the use of
freight trains are 10.9% and 25% of the annual freight transport
demand, respectively. The lower (:math:`%_{fr,boat,min}`) and upper bounds
(:math:`%_{fr,boat,max}`) for the use of freight inland boats are 15.6% and
30% of the annual freight transport demand, respectively. The lower
(:math:`%_{fr,trucks,min}`) and upper bounds (:math:`%_{fr,trucks,max}`) for the use
of freight trucks are 0% and 100% of the annual freight transport
demand, respectively. The bounds and technologies information are
latter summarised in Table
`1.15 <#tbl:freight_vehicles_efficiency>`__.

.. figure:: /images/belgian_data/ts_mob.png
   :alt: Normalised passenger mobility time series over a day. We assume a similar passenger mobility demand over the days of the year.  
   :name: fig:TS_mobPass
   :width: 6cm
   :height: 4cm

   Normalised passenger mobility time series over a day. We assume a
   similar passenger mobility demand over the days of the year.

.. _app:discount_and_interest_rates:

Discount rate and interest rate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To compute their profitability, companies apply a discount rate to the
investment they make. A discount rate is used for both cost of finance
and for risk perception and opportunity cost. The cost of finance is to
be compared with concepts like ‘hurdle rate’ or ‘rate of return’ usually
calculated in accordance to an annual return on investment. Each
individual investment physically occurring in year k, results in a
stream of payments towards the amortization of this investment spread
over several years in the future. The higher the cost of finance (or
hurdle rate), the higher the annual payments spread over the lifetime of
an investment and thus the higher the total cost. The hurdle rate
affects only the investment costs so the impact is bigger for capital
intensive technologies. We consider differentiated hurdle discount rates
for different groups of energy supply and demand technologies,
representing the different risk perception of industry versus
individuals.

According with :raw-latex:`\citet{Meinke-Hubeny2017}` who based their
work on the JRC EU TIMES model :raw-latex:`\cite{simoes2013jrc}` in line
with the PRIMES model :raw-latex:`\cite{EuropeanCommission2016}`, the
discount rate is around 7.5 up to 12% depending on the technologies.
Discount rate cannot be directly converted into interest rate as the
first is fixed by the market and the second is fixed by the central
banks. As the evidence presented in Figure
`1.5 <#fig:path_be_irate_discountrate>`__ indicates, while these two
interest rates tend to move together, they also may follow different
paths from time to time.


.. figure:: /images/belgian_data/path_be_i_rate_and_discount_rate.png
   :alt: Comparison of Belgian interest rate and discount rate. The following rate was chosen to represent the discount rate: floating loans rate over a 1M€ (other than bank overdraft) and up to 1 year initial rate fixation.
   :name: fig:path_be_irate_discountrate

   Comparison of Belgian interest rate and discount rate. The following
   rate was chosen to represent the discount rate: floating loans rate
   over a 1M€ (other than bank overdraft) and up to 1 year initial rate
   fixation.

For the different studies, the real discount rate for the public
investor :math:`i_{rate}` is fixed to 1.5%, which is similar to the floating
loan rate over a million euros (other than bank overdraft) and greater
than the central bank interest rate.

.. _app:BESTD_data_technologies:

Technologies
------------

The technologies are regrouped by their main output types.

Electricity production
~~~~~~~~~~~~~~~~~~~~~~

The following technologies are regrouped into two categories depending
on the resources used: renewable or not.

.. _ssec:app1_renewables:

Renewables
^^^^^^^^^^

.. container::
   :name: foot:GeothermalData

   .. table:: Renewable electricity production technologies, in 2035. Abbreviations: onshore (on.), offshore (off.).

      +-------------+-------------+-------------+-------------+-------------+-------------+-------------+----------+
      |             | :math:`c_   | :math:`c_   | :math:`gwp_ | :math:`li   | :math:`c_   | :math:`f_   | :math:`f_|
      |             | {inv}`      | {maint}`    | {constr}`   | fetime`     | {p}`        | {min}`      | {max}`   |
      +-------------+-------------+-------------+-------------+-------------+-------------+-------------+----------+
      |             | [€          | [€          | [kgCO       |    [y]      |    [%]      |    [GW]     |    [GW]  |
      |             | :sub:`2015` | :sub:`2015` | :sub:`2-eq.`|             |             |             |          |
      |             | /kW         | /kW         | /kW         |             |             |             |          |
      |             | :sub:`e`]   | :sub:`e`/y] | :sub:`e`]   |             |             |             |          |
      +-------------+-------------+-------------+-------------+-------------+-------------+-------------+----------+
      |    Solar    |    870      |    18.8     |    2081     |    25       |    11.9     |    0        |    59.2  |
      |    PV       |    [57]_    |             |    :r       |    :        |    [58]_    |             |    [59]_ |
      |             |             |             |    aw-la    |    raw-l    |             |             |          |
      |             |             |             |    tex:`    |    atex:    |             |             |          |
      |             |             |             |    \cite    |    `\cit    |             |             |          |
      |             |             |             |    {weid    |    e{eur    |             |             |          |
      |             |             |             |    ema_e    |    opean    |             |             |          |
      |             |             |             |    coinv    |    _phot    |             |             |          |
      |             |             |             |    ent_2    |    ovolt    |             |             |          |
      |             |             |             |    013}`    |    aic_t    |             |             |          |
      |             |             |             |             |    echno    |             |             |          |
      |             |             |             |             |    logy_    |             |             |          |
      |             |             |             |             |    platf    |             |             |          |
      |             |             |             |             |    orm_s    |             |             |          |
      |             |             |             |             |    trate    |             |             |          |
      |             |             |             |             |    gic_2    |             |             |          |
      |             |             |             |             |    011}`    |             |             |          |
      +-------------+-------------+-------------+-------------+-------------+-------------+-------------+----------+
      |    On.      |    1040     |    2.9      |    622.9    |    30       |    24.3     |    0        |    10    |
      |    Wind     |    [60]_    |             |    :r       |    :raw     |             |             |    [61]_ |
      |    Tu       |             |             |    aw-la    |    -late    |             |             |          |
      |    rbine    |             |             |    tex:`    |    x:`\c    |             |             |          |
      |             |             |             |    \cite    |    ite{a    |             |             |          |
      |             |             |             |    {weid    |    ssoci    |             |             |          |
      |             |             |             |    ema_e    |    ation    |             |             |          |
      |             |             |             |    coinv    |    _des_    |             |             |          |
      |             |             |             |    ent_2    |    entre    |             |             |          |
      |             |             |             |    013}`    |    prise    |             |             |          |
      |             |             |             |             |    s_ele    |             |             |          |
      |             |             |             |             |    ctriq    |             |             |          |
      |             |             |             |             |    ues_s    |             |             |          |
      |             |             |             |             |    uisse    |             |             |          |
      |             |             |             |             |    s_aes    |             |             |          |
      |             |             |             |             |    _ener    |             |             |          |
      |             |             |             |             |    gie_2    |             |             |          |
      |             |             |             |             |    013}`    |             |             |          |
      +-------------+-------------+-------------+-------------+-------------+-------------+-------------+----------+
      |    Off.     |    4975     |    9.8      |    622.9    |    30       |    41.2     |    0        |    3.5   |
      |    Wind     |    [62]_    |             |    :r       |    :raw     |             |             |          |
      |    Tu       |             |             |    aw-la    |    -late    |             |             |          |
      |    rbine    |             |             |    tex:`    |    x:`\c    |             |             |          |
      |             |             |             |    \cite    |    ite{a    |             |             |          |
      |             |             |             |    {weid    |    ssoci    |             |             |          |
      |             |             |             |    ema_e    |    ation    |             |             |          |
      |             |             |             |    coinv    |    _des_    |             |             |          |
      |             |             |             |    ent_2    |    entre    |             |             |          |
      |             |             |             |    013}`    |    prise    |             |             |          |
      |             |             |             |             |    s_ele    |             |             |          |
      |             |             |             |             |    ctriq    |             |             |          |
      |             |             |             |             |    ues_s    |             |             |          |
      |             |             |             |             |    uisse    |             |             |          |
      |             |             |             |             |    s_aes    |             |             |          |
      |             |             |             |             |    _ener    |             |             |          |
      |             |             |             |             |    gie_2    |             |             |          |
      |             |             |             |             |    013}`    |             |             |          |
      +-------------+-------------+-------------+-------------+-------------+-------------+-------------+----------+
      |    Hydro    |    5045     |    50.44    |    1263     |    40       |    48.4     |    0.38     |    0.38  |
      |    River    |    :ra      |    :ra      |    :r       |    :ra      |             |    :r       |    :r    |
      |             |    w-lat    |    w-lat    |    aw-la    |    w-lat    |             |    aw-la    |    aw-la |
      |             |    ex:`\    |    ex:`\    |    tex:`    |    ex:`\    |             |    tex:`    |    tex:` |
      |             |    cite{    |    cite{    |    \cite    |    cite{    |             |    \cite    |    \cite |
      |             |    assoc    |    assoc    |    {weid    |    assoc    |             |    {swis    |    {swis |
      |             |    iatio    |    iatio    |    ema_e    |    iatio    |             |    s_fed    |    s_fed |
      |             |    n_des    |    n_des    |    coinv    |    n_des    |             |    eral_    |    eral_ |
      |             |    _entr    |    _entr    |    ent_2    |    _entr    |             |    offic    |    offic |
      |             |    epris    |    epris    |    013}`    |    epris    |             |    e_of_    |    e_of_ |
      |             |    es_el    |    es_el    |             |    es_el    |             |    energ    |    energ |
      |             |    ectri    |    ectri    |             |    ectri    |             |    y_sfo    |    y_sfo |
      |             |    ques_    |    ques_    |             |    ques_    |             |    e_sta    |    e_sta |
      |             |    suiss    |    suiss    |             |    suiss    |             |    tisti    |    tisti |
      |             |    es_ae    |    es_ae    |             |    es_ae    |             |    que_2    |    que_2 |
      |             |    s_gra    |    s_gra    |             |    s_gra    |             |    013}`    |    013}` |
      |             |    nde_2    |    nde_2    |             |    nde_2    |             |             |          |
      |             |    014}`    |    014}`    |             |    014}`    |             |             |          |
      +-------------+-------------+-------------+-------------+-------------+-------------+-------------+----------+
      | Geothermal  |    7488     |    142      |    24.9     |    30       |    86       |    0        |    0     |
      | [63]_       |             |             |    :r       |             |    :ra      |             |    [64]_ |
      |             |             |             |    aw-la    |             |    w-lat    |             |          |
      |             |             |             |    tex:`    |             |    ex:`\    |             |          |
      |             |             |             |    \cite    |             |    cite{    |             |          |
      |             |             |             |    {weid    |             |    assoc    |             |          |
      |             |             |             |    ema_e    |             |    iatio    |             |          |
      |             |             |             |    coinv    |             |    n_des    |             |          |
      |             |             |             |    ent_2    |             |    _entr    |             |          |
      |             |             |             |    013}`    |             |    epris    |             |          |
      |             |             |             |             |             |    es_el    |             |          |
      |             |             |             |             |             |    ectri    |             |          |
      |             |             |             |             |             |    ques_    |             |          |
      |             |             |             |             |             |    suiss    |             |          |
      |             |             |             |             |             |    es_ae    |             |          |
      |             |             |             |             |             |    s_ele    |             |          |
      |             |             |             |             |             |    ctric    |             |          |
      |             |             |             |             |             |    ite_2    |             |          |
      |             |             |             |             |             |    012}`    |             |          |
      +-------------+-------------+-------------+-------------+-------------+-------------+-------------+----------+



| Data for the considered renewable electricity production technologies
  are listed in Table `[tbl:renew_elec] <#tbl:renew_elec>`__, including
  the yearly capacity factor (:math:`c_p`). As described in the Section
  `[ssec:lp_formulation] <#ssec:lp_formulation>`__, for seasonal
  renewables the capacity factor :math:`c_{p,t}` is defined for each
  time period. These capacity factors are represented in Figure
  `[fig:TS_Renewables] <#fig:TS_Renewables>`__. For these technologies,
  :math:`c_p` is the average of :math:`c_{p,t}`. For all the other
  electricity supply technologies (renewable and non-renewable),
  :math:`c_{p,t}` is equal to the default value of 1. As the power
  delivered by the hydro river is almost negligible, we take the time
  series of hydro river from Switzerland
  :raw-latex:`\cite{Limpens2019}`.






.. [27]
   [foot:res_elec] Based on average market price in the year 2010 (50
   EUR\ \ :sub:`2010`/MWh, from
   :raw-latex:`\cite{epex_spot_swissix_????}`). Projected from 2010 to
   2035 using a multiplication factor of 1.36
   :raw-latex:`\cite{prognos_ag_energieperspektiven_2012}`. For security
   of supply reason, the availability is limited to 30% of yearly
   electricity EUD (See Section
   `[ssec:be_policies] <#ssec:be_policies>`__).

.. [28]
   [foot:t22_resources] GWP100a-IPCC2013 metric: impact associated to
   production, transport and combustion, see
   :raw-latex:`\cite{Moret2017PhDThesis}`

.. [29]
   Based on 1.49 CHF\ \ :sub:`2015`/L (average price in 2015 for
   gasoline 95 in Switzerland)
   :raw-latex:`\cite{swiss_federal_office_of_statistics_sfos_ipc_2016}`.
   Taxes (0.86 CHF\ \ :sub:`2015`/L,
   :raw-latex:`\cite{beuret_evolution_2016}`) are removed and the
   difference is projected from 2015 to 2035 using a multiplication
   factor of 1.24 :raw-latex:`\cite{european_commission_energy_2011}`.
   In line with :raw-latex:`\cite{simoes2013jrc}`.

.. [30]
   Based on 1.55 CHF\ \ :sub:`2015`/L (average price in 2015)
   :raw-latex:`\cite{swiss_federal_office_of_statistics_sfos_ipc_2016}`.
   Taxes (0.87 CHF\ \ :sub:`2015`/L,
   :raw-latex:`\cite{beuret_evolution_2016}`) are removed and the
   difference is projected from 2015 to 2035 using a multiplication
   factor of 1.24 :raw-latex:`\cite{european_commission_energy_2011}`.
   In line with :raw-latex:`\cite{simoes2013jrc}`.

.. [31]
   Based on 0.705 CHF\ \ :sub:`2015`/L (average price in 2015 for
   consumptions above 20000 L/y)
   :raw-latex:`\cite{swiss_federal_office_of_statistics_sfos_indice_2016-1}`.
   Taxes (0.22 CHF\ \ :sub:`2015`/L,
   :raw-latex:`\cite{beuret_evolution_2016}`) are removed and the
   difference is projected from 2015 to 2035 using a multiplication
   factor of 1.24 :raw-latex:`\cite{european_commission_energy_2011}`.
   In line with :raw-latex:`\cite{simoes2013jrc}`.

.. [32]
   [foot:RES_cost_JRC] Based on the EUC estimated cost of resources in
   2030, see Table 5 from :raw-latex:`\cite{simoes2013jrc}`.

.. [33]
   Assuming that the energy content can be assimilated to plastics and
   extended to LFO.

.. [34]
   Average of the data points for 2035 in
   :raw-latex:`\cite{f._ess_kosten_2011}`, accounting for the efficiency
   of nuclear power plants (Table
   `[tbl:nonrenew_elec] <#tbl:nonrenew_elec>`__).

.. [35]
   [foot:bry_electrofuels] Data extrapolated from
   :raw-latex:`\cite{brynolf2018electrofuels}`



































































































This version of the model has minor improvments compared to EnergyScope v2.1 [GL thesis].
The documentation is available in Appendix C of `Thesis <https://www.researchgate.net/profile/Gauthier-Limpens/publication/352877189_Generating_energy_transition_pathways_application_to_Belgium/links/60dd7713458515d6fbef9700/Generating-energy-transition-pathways-application-to-Belgium.pdf>`_ 
However, some changes have been made and are detailed hereafter.

Non-energy demand implementation
--------------------------------

Non energy demand represents the use of energy carriers as feedstocks. The best examples are plastics and fertilisers. 
The first uses hydrocarbons as material, the second require ammonia, which is produced from natural gas (steam methan reforming and then haber-bosch).

While the former version proposes the implementation of final energy demand (i.e. hydrocarbons or natural gas) for the non-energy demand, this version proposes the use of three end-use demand.
Based on the works of Rixhon et al. [rixhon2021comprehensive], the NED accounts for three types of end use demand: ammonia, methanol and high-value chemicals (HVC).
Thus, the conversion pathways to produce all these feedstocks were implemented.

The following figure represents the different conversion pathways. The new resources, technologies and end-use demand are represented.
Hereafter, we detail the characteristics for each technologies:

.. image:: /images/NED_v2.2.png

In 2015, the NED (in TWh) was split in 77.9% of HVC, 19.2% of ammonia and 2.9% of methanol. We suppose these shares to be constant during the transition.
The Non-energy demand in 2035 for the NED is 53 109 GWh


Resources updated:
------------------

In this version, some fuels have been added and the projection prices of renewable fuels in 2035 have been updated. 


New fuels:
~~~~~~~~~~

They are: Ammonia, Ammonia_re, Methanol, Methanol_re, h2, h2_re

To avoid ambiguity between renewable fuels and their fossil equivalent, the ambiguous resources are followeb by '_re' if they are issued from renewable feedstocks.
Thus, we have gas and gas_re, or h2 and h2_re. Gas refers to what is usually called 'natural gas', while gas_re refers to methane from biogas, methanation of renewable hydrogen,...


Renewable fuels prices:
~~~~~~~~~~~~~~~~~~~~~~~

The estimation of previous fuels price were made based on the works of Brynolf et al. [BRYNOLF] in 2018. Since, a specific study for the Belgian case has been conducted by a consortium of industries [H2coalitie], which estimate new prices for the imports.
The following table summarise all the input data for the resources (update of Table C.2 in `Thesis <https://www.researchgate.net/profile/Gauthier-Limpens/publication/352877189_Generating_energy_transition_pathways_application_to_Belgium/links/60dd7713458515d6fbef9700/Generating-energy-transition-pathways-application-to-Belgium.pdf>`_ ).


.. csv-table:: Resources prices:  
    :header: Resource, availability,  global warming potential, price
    :widths: 15 10 30 10

    ,``avail``,``gwp_op``,``c_op``
    , [GWh/y], [kt_CO2eq/GWh], [M€_2015/GWh]
    Electricity imported,27568,0.206,0.084
    Gasoline,Infinity,0.345,0.082
    Diesel,Infinity,0.315,0.080
    Bio-ethanol,Infinity,0,0.111
    Bio-diesel,Infinity,0,0.120
    Light fuel oil,Infinity,0.312,0.060
    Gas (fossil),Infinity,0.267,0.044
    Gas (renewable),Infinity,0,0.118
    Wood,23400,0.012,0.033
    Wet biomass,38900,0.012,0.006
    Coal,33355,0.401,0.018
    Uranium,Infinity,0.004,0.004
    Waste,17800,0.150,0.023
    Hydrogen (fossil),Infinity,0.364,0.088
    Hydrogen (renewable),Infinity,0,0.119
    Ammonia (fossil),Infinity,0.285,0.076
    Methanol (fossil),Infinity,0.350,0.082
    Ammonia (renewable),Infinity,0,0.082
    Methanol (renewable),Infinity,0,0.111  



Technologies updates:
---------------------

New technologies have been added, related to the new fuels.
As an example, methanol can now be used for cars or trucks. 
These new technologies have no restriction of deployment.

The offshore wind capacity has been increased from 3.5 to 6 GW due to recent annoucement of the  
`Belgian offshore plateform <https://www.belgianoffshoreplatform.be/fr/>`_ .

Bibliography:
-------------

- [1] Limpens, G. (2021). Generating energy transition pathways: application to Belgium (Doctoral dissertation, UCL-Université Catholique de Louvain).
- [2] Rixhon, Xavier and Colla, Martin and Verleysen, Kevin and Tonelli, Davide and Limpens, Gauthier. Comprehensive integration of the non-energy demand within a whole-energy system : Towards a defossilisation of the chemical industry in Belgium. Proceedings ECOS2021.
- [3] Brynolf, S., Taljegard, M., Grahn, M., & Hansson, J. (2018). Electrofuels for the transport sector: A review of production costs. Renewable and Sustainable Energy Reviews, 81, 1887-1905. 
- [4] Hydrogen Import Coalition. Shipping sun and wind to Belgium is key in climate neutral economy. 2020