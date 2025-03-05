# Blood Donation Campaign Dashboard documentation!

## Description

This is a comprehensive dashboard, implemented in python for the visualization and analysis of blood donation campaign data. The dashboard will be used by campaign organizers for addressing key questions, helping them make data-driven decisions to improve the success of future blood donation campaigns.

## Commands

The Makefile contains the central entry points for common tasks related to this project.

### Syncing data to cloud storage

* `make sync_data_up` will use `aws s3 sync` to recursively sync files in `data/` up to `s3://s3://abo-blood-donation-dataset/data/`.
* `make sync_data_down` will use `aws s3 sync` to recursively sync files from `s3://s3://abo-blood-donation-dataset/data/` to `data/`.


