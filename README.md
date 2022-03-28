# comp0016miemie_vm
How to run the NLP Engine 

Step 1. Log in the Azure VM

1.Please open your terminal and enter: ssh uclteam43@51.142.241.173
2.Please enter the password: UCLmiemie2021

Step 2. Run the NLP Engine

Please enter: cd comp0016miemie_vm
Please enter: cd src

Then run the lines below

Scraping Modules: 

First, we can initialise departmental data, which is necessary to perform prior to scraping. It can be done by running the command below: 

python3 global_controller.py MOD initialise

Furthermore, it is vital to reset the current module data to ensure the end result only reflects the current teaching activity at UCL. This is done by running the following command: 

python3 global_controller.py MOD resetDB

Lastly, to reflect the current student population data, keep the file ”studentsPerModule.csv” up-to-date in directory
src/main/MODULE_CATALOGUE/STUDENTS_PER_MOD. To synchronise that data with the database run the following command: 

python3 global_controller.py MOD updateStudentCount

Finally, module scraping can be performed. Ensure the MySQL credentials are valid and up-to-date in config.ini file (under SQL_SERVER section) and run the following command to freshly scrape the UCL module catalogue data: 

python3 global_controller.py MOD scrape

Finally, module scraping can be performed. Ensure the MySQL credentials are valid and up-to-date in config.ini file (under SQL_SERVER section) and run the fol
Once finished, the data is automatically synchronised with the database, and can be viewed in the ModuleData table through any database management system by inputting login credentials found in config.ini SQL_SERVER section. It should have the following appeal:


Scraping Publications 

Prior to scraping, firstly ensure the file titled “cleaned_RPS_export_2015.csv” in directory src/main/SCOPUS/GIVEN_DATA_FILES is up-to-date. The file should contain a column titled “DOI”. 
The scraper examines given DOIs, compares them to existing records and scrapes only those not already present in the database. It is vital for the file to retain its structural integrity to avoid any unexpected script errors. Secondly, follow instructions below to setup Scopus API key and initiate scraping procedure: 
1.Go to: https://dev.elsevier.com/documentation/AbstractRetrievalAPI.wadl
2.Locate My API Key section on the top right 
3. Sign in with your institution (needs to verify affiliation identifier) 
4. Create API key (tick agreement boxes and submit) 
5. *Run the following command: python3 global_controller.py SCRAPE_PUB
6. When prompted to enter your API key, copy it from the website and enter it 
7. Click enter once more to skip the Authtoken authentication prompt 
8. This will create the scopus config.ini file so that this process doesn’t have to be
repeated for future scrapes 

*Once the Scopus API key has been set up, ensure that you are on a UCL network 
(either using UCL WI-FI or connected to a UCL virtual machine). It can also be 
achieved via UCL VPN (instructions). 

Automatic operation
To run the NLP engine automatically, we used crontab in our virtual machine. The
engine will be run automatically every 1st of January.

View current crontab automatic command:
                               crontab -l

View and change the crontab command:
                              crontab -e

Using the Engine 

To run the tool, examine the list of available commands, each dedicated to a specific action. Note running a command impacts files, as well as certain database contents (possibility of overwriting existing values). Chronologically coherent sequence of commands is outlined below. Loading the publication and module data: 

python3 global_controller.py LOAD publications
python3 global_controller.py LOAD modules

Train the LDA for SDGs and/or IHEs and/or HAs

python3 global_controller.py NLP run_LDA_SDG
python3 global_controller.py NLP run_LDA_IHE
python3 global_controller.py NLP run_LDA_HA

Perform string-matching for SDGs or HAs (skip if only focusing on IHEs)

python3 global_controller.py NLP module_string_match
python3 global_controller.py NLP ha_string_match
python3 global_controller.py NLP scopus_string_match_SDG
python3 global_controller.py NLP scopus_string_match_IHE
python3 global_controller.py NLP scopus_string_match_HA

Use SDG and HA LDA results to classify publications (skip if only focusing on IHEs)

python3 global_controller.py NLP predict_scopus_data

Prepare pickled dataset for SVM training (for SDGs and/or IHEs and/or HAs)

python3 global_controller.py NLP create_SDG_SVM_dataset
python3 global_controller.py NLP create_IHE_SVM_dataset
python3 global_controller.py NLP create_HA_SVM_dataset

Train the SVM for SDGs and/or IHEs and/or HAs

python3 global_controller.py NLP run_SVM_SDG
python3 global_controller.py NLP run_SVM_IHE
python3 global_controller.py NLP run_SVM_HA

Validate SVM SDG/HA results against string-match ((skip if only focusing on IHEs)

python3 global_controller.py NLP validate_sdg_svm
python3 global_controller.py NLP validate_ha_svm


Once publication and module data are scraped, synchronise MongoDB with PostgreSQL 

          python3 global_controller.py SYNC synchronize_raw_mongodb

After LDA & SVM training, synchronise results with PostgreSQL

     python3 global_controller.py SYNC synchronize_mongodb
 
After LDA & SVM training, use publication classification to update user data + bubble chart data 

python3 global_controller.py SYNC synchronize_bubble


















