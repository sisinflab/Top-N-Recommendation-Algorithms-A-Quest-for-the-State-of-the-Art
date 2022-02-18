# Top-N Recommendation Algorithms: A Quest for the State of the Art

This is the repository for the paper _Top-N Recommendation Algorithms: A Quest for the State of the Art_, under review at ACM UMAP 2022.

The experiments reported in this paper were done with the help of the recent **Elliot** framework published by Anelli et al. We therefore also refer you to the official GitHub [page](https://github.com/sisinflab/elliot) and [documentation](https://elliot.readthedocs.io/en/latest/) of this framework.

This repository contains the configuration files and datasets needed for reproducing the experiments analyzed in our work.
In particular, the configuration file in the `config_files` folder contains the experiment setup adopted for each model under analysis. For further details on exploration ranges and hyperparameters for the best models please refer to [the supplemental material](./Recommender_Systems_State_of_the_Art_Additional_Material.pdf).

### Installation guidelines
Elliot requires Python version 3.8 or later.

Elliot requires TensorFlow version 2.3.2 or later. If you want to use Elliot with a GPU, please ensure that CUDA or cudatoolkit version is 7.6 or later. This requires NVIDIA driver version >= 10.1 (for Linux and Windows10).

##### Install from source

##### CONDA
```bash
git clone https://github.com//sisinflab/elliot.git && cd elliot
conda create --name elliot_env python=3.8
conda activate elliot_env
pip install --upgrade pip
pip install -e . --verbose
```

##### VIRTUALENV
```bash
git clone https://github.com//sisinflab/elliot.git && cd elliot
virtualenv -p /usr/bin/python3.8 venv # your python location and version
source venv/bin/activate
pip install --upgrade pip
pip install -e . --verbose
```


### Datasets
In the folder `./data/` you find the files for the datasets (_Movilens 1M_, _Amazon Digital Music_, _Epionions_) used in our experiments. We have included in the folder both the original file for each dataset and the filtered and split version used in our experiments.
The following table shows the statistics of the original datasets and the filtering operations applied for each of them.

| Dataset                   | Original transactions | Original users            | Original items        |p-core                     | threshold             |
|---------------------------|-----------------------|---------------------------|-----------------------|---------------------------|-----------------------|
| **Movielens 1M**          | 1000209               | 6040                      | 3706                  | 10                        | 4                     |
| **Amazon Digital Music**  | 1584082               | 840372                    | 45992                 | 5                         | 4                     |
| **Epinions**              | 300548                | 8514                      | 8510                  | 2                         | /                     |

### Running and reproducing experiments

To reproduce the experiments from our analysis, start the virtual environment and run the following command
```bash
source venv/bin/activate
python run_reproducibility_study.py
```
To set the dataset for an analysis,  edit the `dataset` field in the configuration file according to the following naming scheme


| Dataset                   | Dataset config name        |
|---------------------------|----------------------------|
| **Movielens 1M**          | movielens_1m               |
| **Amazon Digital Music**  | amazon_music               |
| **Epinions**              | epinions                   |




