# -*- coding: utf-8 -*-
"""
This file defines a dictionary with global variables to be used in EnergyScope such as fuels, technologies, etc.
"""
import datetime

commons = dict()

commons['logfile'] = str(datetime.datetime.now()).replace(':', '-').replace(' ', '_') + '.energyscope.log'
