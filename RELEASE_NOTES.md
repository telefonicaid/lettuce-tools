WWhat's New
==========

v0.0.6
------

* *Improvement*:New project structure and distribution

v0.0.5
------

#### Logs_checking

* *New feature*:Logs parser library to create logs validation scenarios first version


v0.0.4
------

#### Jirasync

* *Improvement*: New testcase executions are not created in case status remains the same, old testcase execution is updated instead.

v0.0.3
------

#### Lettucetdaf

* *Bug*: Fixed some cases where unexpected features would be executed because of the coincidence between its filename and path
* *New feature*: Added some metrics (US total number, TC total number, TCs per US)

---

#### Jirasync

* *Improvement*: Added a way to include component parameter on testcases and testcases executions.
* *Improvement*: Included Jira parameter to check whether to update testcase executions or not.
* *New feature*: Added Jira decorator.
* *New feature*: Included Exception trace on failing testcase executions

v0.0.2
------

#### Lettucetdaf

* *Improvement*: Added a way to define the features to execute
* *Improvement*: Make jirasync only execute for features and epics selected in arguments

---

#### Jirasync

* *Bug*: Fixed the identification of the jira key of the feature in both the .feature files name and the scenarios.
* *Bug*: Fixed the separation of the different parts of the scenario description (prerequisites, procedure, result, dataset).
* *Improvement*: Improved the sanitization of the description of the user story.
* *Improvement*: The content of the .feature files before the first "Feature" statement now is always kept.
* *Improvement*: Added a way to keep the old feature summary and description in the .feature files if getting them from Jira fails.
* *Improvement*: Added a transition to "Block" in the test case executions.
* *New feature*: Added the option to pass the folder where to look for the .feature files as parameter.

v0.0.1
------
* First version