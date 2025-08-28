In order for the analysis scripts to run properly, the necessary Python libraries and packages must be installed. To ensure reproducibility and keep dependencies organized, I opted to create a virtual environment called “thesis.”

The scripts specifically rely on the following:
	•	pandas for loading, cleaning, and manipulating data
	•	numpy for numerical operations and handling of missing values
	•	scipy (especially scipy.stats) for statistical testing, including t-tests, chi-square tests, Fisher’s exact test, binomial tests, and Spearman correlations
	•	openpyxl which allows pandas to read Excel files
	•	Standard Python libraries (re for regular expressions and math for basic mathematical functions), which are included in Python by default
For easier setup, all required packages can also be listed in a requirements.txt file so that they can be installed at once using the command pip install -r requirements.txt.
