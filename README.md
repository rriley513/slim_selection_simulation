# slim_real_data_generation
uses the Messer Lab's SLiM application for producing synthetic genetic data

1. Run `get_recos.py` with arguments of the path to your recombination rate data files, and the path to save a newline-separated list of recombination rates. Adjust the variable COUNT as needed.
2. Run `bash make_exp_trees.sh` with arguments in the following order: the recombination rates text file, the parameters for your SLiM file (comma-separated, no spaces), the path to the output folder, the path to the slim file, and the strength of selection (unused if no selection)
3. Run `process_trees.py`
4. Run `combine_slim_data.py` as necessary