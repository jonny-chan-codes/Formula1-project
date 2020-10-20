# Formula1-project
Data-files and code used for doing strategy analysis for my Formula 1 based masters project
Its a bit of a mess but I've just uploaded everything that I had at the end of writing the dissertation.

Please read the dissertation_2nd_draft.pdf for the final paper. It contains a very detailed walkthrough of the methodologies, my thought process 
and analysis that I carried out using the tools that I developed. 

data_gather.py is the script used to load the dataframes in the datafolder and make new and more useful dataframes.

sample_Race.py contains the functions used to sample the racing data from a particular driver in a particular race. 

modeler3.py is the script where I define and fit the model I fit the data to gather the parameters of the model. 

optimiser_integration.py is the script where I find the optimal race strategy using a brute force search. 

refulling_optimiser.py is the same as optimiser_integration but modified for the scenario that refuelling is allowed. 

