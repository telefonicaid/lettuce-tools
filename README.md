Lettuce Tools
==========

TDAF Lettuce Tools are a set of tools and utilities that extend the lettuce out of the box features fill some of the gaps detected in the projects.

To create a dependency in your project requirements to install it througth pip add the following line to your file:

	git+https://visitor:visitor@pdihub.hi.inet/TDAF/tdaf-lettuce-tools.git@develop#egg=tdaf_lettuce_tools

To install it manually, clone the repository and run "python setup.py install". That will install the TDAF Lettuce tools in your python environment.
	
Lettuce Tools are composed by the following modules:

### Jirasync

* **jirasync** synchronizes information between Jira and lettuce .features files.

To use jirasync copy the vanilla file to your .features files root path and configure in it the values for your user and project. Then run "python jirasync.py". jirasync can also be invoked with the path of a folder as its main argument. In that case, only the .feature files of that folder and its sub-folders will be processed.

### Lettuce_Tools

* **lettuce_tools** is a lettuce wrapper that enables different executions of test depending on the input parameters.
* **check_results** parses xunit lettuce output and process result to generate QA metrics

### Log_checking

* **log_utils** is a module that can be used in the acceptance tests of any TDAF application, as long as they are developed with Lettuce, to check whether a log file has the right format according to the current specification. 

It can also search for a specific log entry that matches a set of given parameters and values. See the public methods inside the module for details.

### Mock

* **mock** is a module that can be used in the acceptance tests of any TDAF application, as long as they are developed with Lettuce, to implement a configurable http REST mock. 

Its main features are: configure a response on a given endpoint, serve configured responses, maintains checkable list of requests and responses. 

An overridable json properties file is given. A test project is provided as well.
