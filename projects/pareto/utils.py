import yaml
import os
import shutil

from typing import Dict

import energyscope as es


def empty_temp(temp_dir: str):
    shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)


def load_config(config_fn: str) -> Dict:

    # Load parameters
    cfg = yaml.load(open(config_fn, 'r'), Loader=yaml.FullLoader)

    # Extend path
    for param in ['case_studies_dir', 'user_data', 'developer_data', 'temp_dir', 'model_path', 'step1_output']:
        cfg[param] = os.path.join(cfg['energyscope_dir'], cfg[param])

    return cfg


def load_data(cfg: Dict):

    all_data = es.import_data(cfg['user_data'], cfg['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in cfg['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = cfg['Technologies']['f_min'][tech]
    # Modify the maximal capacities of some technologies
    if 'f_max' in cfg['Technologies']:
        for tech in cfg['Technologies']['f_max']:
            all_data['Technologies']['f_max'].loc[tech] = cfg['Technologies']['f_max'][tech]
    # Modify the maximal potential of some resources
    if 'Resources' in cfg and 'avail' in cfg['Resources']:
        for res in cfg['Resources']['avail']:
            all_data['Resources']['avail'].loc[res] = cfg['Resources']['avail'][res]

    return all_data
