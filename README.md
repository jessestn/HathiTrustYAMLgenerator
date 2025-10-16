# YAMLgenerator  

## Python script and documentation adapted from [yaml-generator-for-hathitrust](https://github.com/ruthtillman/yaml-generator-for-hathitrust) created by [ruthtillman](https://github.com/ruthtillman)  

### This repository includes a Python script which uses an input CSV file to generate a YAML metadata file or files for uploading material to the **[HathiTrust digital library](https://www.hathitrust.org/)**.  
The purpose of adapting the Python script and documentation from the GitHub repository referenced above was to update and customize them for use at the **[University of Washington Libraries Preservation Services](https://lib.uw.edu/preservation/)** unit.  

### The overall workflow is as follows, and is detailed in the **[how-to](https://github.com/ries07uw/HathiTrustYAMLgenerator/blob/master/HowTo.md)** file provided in this repository:
- **[Python 3.x](https://www.python.org/downloads/)** must be installed on the computer that will be used to generate YAML files, and the **[csv-to-yml.py](https://github.com/jessestn/HathiTrustYAMLgenerator/blob/master/csv-to-yml.py)** script will need to be downloaded as well.  
- Create a copy of the **[data-entry spreadsheet template](https://github.com/jessestn/HathiTrustYAMLgenerator/blob/master/YAML_DataEntryTemplate.csv)** and enter information about the digitized item, the digital capture process, etc. 
- Save the completed spreadsheet containing information about one or more digitized items as a CSV file.
- Run the [csv-to-yml.py](https://github.com/jessestn/HathiTrustYAMLgenerator/blob/master/csv-to-yml.py) script with the path to the csv file as an argument.
- The YML files will be automatically placed in the same folder as the csv file. 

- Confirm generated files and package along with page image files, OCR files, etc. for upload to the HathiTrust.  

### Next: [How to record item information in a spreadsheet and process this information to generate YAML files](HowTo.md).

Bug fixes:
This is a modified csv-to-yml.py script that makes several fixes.

1.
It makes sure that the times in "Scan Time HH:MM" field in the csv have been properly entered. Sometimes Excel will strip the leading zero on 24hr times. Example: 08:45 will be exported as 8:45. This will cause the Hathi ingest to reject the YML file in the SIP. The Hathi SIP Validator does not catch this error. 
The script now fixes times that are not properly formated but properly formated times or times with correct 4 digits (11:45) will be left alone. 

2.
Instead of asking for the paths of the csv file and destination path for the generated YML files, the user adds the csv file location to the command line arguments and the YML files are automatically placed in that same folder. 
