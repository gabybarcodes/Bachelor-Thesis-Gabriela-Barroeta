# Bachelor Thesis: The Influence of Buy Now, Pay Later (BNPL) Services on Consumer Trust and Brand Perception

Welcome to the repository for my Bachelor thesis, "The Influence of Buy Now, Pay Later (BNPL) Services on Consumer Trust and Brand Perception among Gen Z and Millennials." This repository contains the raw data and three code scripts used to test the main hypothesis and six subhypotheses outlined in my research.

## Project Overview

This project investigates how BNPL services impact consumer trust and brand perception. The code files provided here are used to analyze survey data and validate three main hypotheses and six subhypotheses.

## Overall Summary and Context

The Google Forms survey results were downloaded as a Microsoft Excel file (.xlsx) named “data_survey.xlsx” where the data preparation steps were initiated. Additionally, a separate Microsoft Excel worksheet titled “data_survey_for_python.xlsx” was created for Python to analyse the data, without looking over different sheets.

## Summary “data_survey.xlsx”:

The ‘Total’ sheet is the original export from the Google Form survey; this raw data was formatted into a Table for clarity and analysis, then it was cleaned to address incomplete entries and correct country names. 

The second sheet, ‘Overview Analysis’ provides an overall summary to offer an initial grasp of the results. 
The third sheet, ‘Gen Z and Millennials’ contains the table from the first sheet, copy-pasted and filtered by the ‘Age’ column to focus on the target groups: aged 18 to 44. Further, an additional column named ‘Financial_Stability’ in cell X1 was added using an Excel formula to identify financially stable customers, in order to test hypothesis H2, which proposes that brands avoiding BNPL will be preferred by financially stable or high-status shoppers.  If a participant selected the option ‘Pay the full $200 at once.’ as their response to the final question in the Google survey, they were marked as financially stable (assigned a value of 1). All other responses were considered not financially stable (assigned a value of 0). 
The formula used for the new column was: =IF(EXACT(TRIM(CLEAN(W2));'Pay the full $200 at once.);1;0)

The fourth sheet, ‘Gen Z and Millennials analysis’ takes all the information from the third sheet. Here, a general analysis was conducted, including the total count of participants, distribution by country, calculation of means (averages), and the application of gradient fill data bars to facilitate visual interpretation of the results.

Finally, the sheet called ‘Gen Z and Millennials’ (third sheet) was copy-pasted into a new Excel file to facilitate easier data manipulation and analysis in Python. This new Excel is called “data_survey_for_python.xlsx”. This last one mentioned, had no further manipulation whatsoever.


## Repository Contents

- `data/`: Raw data collected through surveys
- `code/`: Three scripts for hypothesis testing and data analysis

## License

All content in this repository is released under the Creative Commons Zero v1.0 Universal (CC0) license. This means you are free to use, share, and adapt the data and code without restriction.
