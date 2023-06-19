# LandBOSSE

## Welcome to LandBOSSE!

The Land-based Balance-of-System Systems Engineering (LandBOSSE) model is a systems engineering tool that estimates the balance-of-system (BOS) costs associated with installing utility scale wind plants (10, 1.5 MW turbines or larger). It can execute on macOS and Windows. At this time, for both platforms, it is a command line tool that needs to be accessed from the command line.

The methods used to develop this model (specifically, LandBOSSE Version 2.1.0) are described in greater detail the following report:

Eberle, Annika, Owen Roberts, Alicia Key, Parangat Bhaskar, and Katherine Dykes.
2019. NREL’s Balance-of-System Cost Model for Land-Based Wind. Golden, CO:
National Renewable Energy Laboratory. NREL/TP-6A20-72201.
https://www.nrel.gov/docs/fy19osti/72201.pdf.

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

### Operation after the installation

Review the installation instructions on how to activate a virtual environment, if you haven't already.

Then, read the [Operation and Folder Structure](installation_instructions/operation_and_folder_structure.md) for details on running the command that executes LandBOSSE from the command line.
