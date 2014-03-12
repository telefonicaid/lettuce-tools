from jira_config import Jira_Config
import features_manager
import os
import argparse

jira_project=Jira_Config("your project","your component","your user","your pass")

parser = argparse.ArgumentParser( \
	description="Updates Jira with the tests defined in the .feature files")
parser.add_argument("folder", type=str, nargs="?", default="./", \
	help="Folder to walk through looking for .feature files to be processed")
args = parser.parse_args()

for root,dirs,list_files in os.walk(args.folder):
    for file in list_files:
        if file.endswith(".feature"):
           features_manager.update_feature(root,file,jira_project)
