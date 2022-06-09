# managebwmonitoring
Prisma SDWAN script to manage BW Monitoring Configuration at one or more sites

#### Synopsis
Script to manage BW Monitoring setting on Prisma SDWAN Sites. Enable or Disable BW Monitoring on all circuits on a single site or all sites, using the special keyword ALL_SITES.


#### Requirements
* Active Prisma SDWAN Account
* Python >=3.6
* Python modules:
    * CloudGenix Python SDK >= 6.0.1b1 - <https://github.com/CloudGenix/sdk-python>
* ProgressBar2

#### License
MIT

#### Installation:
 - **Github:** Download files to a local directory, manually run `getsites.py`. 

### Usage:
1. Enable BW Monitoring on all circuits for a single site
```
./bwmonitoring.py -S <sitename> -B True
```

2. Disable BW Monitoring on all circuits for a single site
```
./bwmonitoring.py -S <sitename> -B False
```

3. Enable BW Monitoring on all circuits for ALL sites
```
./bwmonitoring.py -S ALL_SITES -B True
```

4. Disable BW Monitoring on all circuits for ALL sites
```
./bwmonitoring.py -S ALL_SITES -B False
```


Help Text:
```angular2
Tanushrees-MacBook-Pro:managebwmonitoring$ ./bwmonitoring.py -h
usage: bwmonitoring.py [-h] [--print-lower] [--controller CONTROLLER] [--email EMAIL] [--password PASSWORD] [--insecure] [--noregion] [--sdkdebug SDKDEBUG] [--sitename SITENAME] [--bwmon BWMON]

Manage Bandwidth Monitoring (v1.0)

optional arguments:
  -h, --help            show this help message and exit

custom_args:
  My Custom Args

  --print-lower         Print all in lower case

API:
  These options change how this program connects to the API.

  --controller CONTROLLER, -C CONTROLLER
                        Controller URI, ex. https://api.elcapitan.cloudgenix.com

Login:
  These options allow skipping of interactive login

  --email EMAIL, -E EMAIL
                        Use this email as User Name instead of cloudgenix_settings.py or prompting
  --password PASSWORD, -PW PASSWORD
                        Use this Password instead of cloudgenix_settings.py or prompting
  --insecure, -I        Do not verify SSL certificate
  --noregion, -NR       Ignore Region-based redirection.

Debug:
  These options enable debugging output

  --sdkdebug SDKDEBUG, -D SDKDEBUG
                        Enable SDK Debug output, levels 0-2

Config:
  These options are to provide site and BW monitoring details

  --sitename SITENAME, -S SITENAME
                        Name of the Site. Or use keyword ALL_SITES
  --bwmon BWMON, -B BWMON
                        Enable or Disable BW Monitoring. Allowed values: True or False

```

#### Version
| Version | Build | Changes |
| ------- | ----- | ------- |
| **1.0.0** | **b1** | Initial Release. |


#### For more info
 * Get help and additional Prisma SDWAN Documentation at <https://docs.paloaltonetworks.com/prisma/prisma-sd-wan>
 
