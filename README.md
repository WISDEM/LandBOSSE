# LandBOSSE

## Welcome to LandBOSSE!

LandBOSSE is a system to model the balance of station (BOS) costs of wind plants at utility scale (10 1.5 MW turbines or larger.) It can execute on macOS and Windows. At this time, for both platforms, it is a command line tool that needs to be accessed from the command line.

This repository accompanies the report entitled "NREL’s Balance-of-System Cost Model for 
Land-Based Wind"

## User Guides

First, read the technical report to understand the big picture of LandBOSSE. In the technical report, you will find process diagrams, equations and the modules that implement them. Then, come back to this documentation and read the user guide.

In brief, LandBOSSE takes `.xlsx` spreadsheets, reads input data from tabs on the spreadsheets, and writes the results to an output `.xlsx` file. There are three sections in the user guide to demonstrate how to perform these steps.

The user guide comes in three parts:

1. Software installation,

2. Input data configuration, and

3. Output data analysis.

### Software Installation

There are two options depending on whether you are a developer or an end user and what operating system you are running.

- **Windows end-user**: If you run the Microsoft Windows operating system and aren't setting up as a developer who is going to be modifying the core library, these instructions are for you. [Find out how to configure Windows for end users.](installation_instructions/windows_end_user.md)

- **macOS end user** and **macOS developer**: If you run the macOS operating system, either as an end-user or as a developer, these instructions are for you. Both developers and end-users will need most of the steps. [Find out how to configure macOS for end users and developers.](installation_instructions/macos_developer.md)

### Input data configuration

Input into the model happens on two `.xlsx` spreadsheets.

The first spreadsheet holds multiple rows, with each row specifying simple and high level variables that control the model. For example, number of turbines. Since each project uses only one row on the spreadsheet, this first spreadsheet can hold references to multiple projects.

The second spreadsheet is a collection of tabs where each tab holds a table of data used by the model. For example, one of the tables holds cable specifications and another table holds crane specifications. Multiple projects can use the same specifications contained on this spreadsheet.

These spreadsheets are tied together in the first spreadsheet. Each row in the first spreadsheet creates a project name, and this project name is used to specify the second spreadsheet for the same project.

### Output data analysis

Output from the model is written to one `.xlsx` spreadsheet. It contains the tabs `details` and `costs_by_module_type_operation`. The latter is a cost breakdown from the various modules. The former is everything the model calculates during operation, including many values that are not monetary values.
