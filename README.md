# Contents
This repository contains scripts for
1. uploading to a Dataverse server (`dvpost`)
2. cloning a Dataverse setup (sub-dataverses, groups and roles) to another Dataverse server (`dvclone`)
3. gathering statistics about file types and sizes (`dvstats`)
4. converting a statistics file (SPSS or SAS) to a ZIP file that contains the data in CSV form, plus a codebook
   (`stats2scv.py`)

`dvstats --filesize` prints to standard output a CSV file with the file contents of all datasets.
This can be used to calculate storage sizes per dataverse, for example.

`dvstats --status` prints to standard output a CSV file with the status and authors of all datasets.
This can be used to find unpublished datasets, for example.

All scripts use a simple interface class `dave` (**da**ta**ve**rse) that uses the Dataverse native API.

# Installation
There is one dependency: requests, a Python module that offers a simple and elegant HTTP interface.
Install this with (in a virtual environment, or globally):

```pip install requests```

# Configuration
All scripts assume that the API keys can be found in a configuration file `~/.config/dataverse.json`
in the home directory of the user. This configuration file should look like this:

```
{
"production": {"url": "https://dataverse.nl",      "key": "..."},
"demo":       {"url": "https://demo.dataverse.nl", "key": "..."}
}
```
