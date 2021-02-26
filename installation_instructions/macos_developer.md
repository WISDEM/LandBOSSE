# macOS developer installation guide

## Audiences

Both end users and developers have a similar installation experience of LandBOSSE. Developers just have a couple more steps that are at the bottom of this document and are marked as such.

## LandBOSSE is a command line program

In its current version, LandBOSSE is a command line program. You access it from terminal.

## Anaconda Installation

This installation guide assumes you have a Python 3.7 or later version of the Anaconda distribution of Python installed. If you aren't using Anaconda you can modify these instructions, but those modifications aren't explained here.

[Download the latest macOS version of Anaconda with Anconda 3.7 or later](https://www.anaconda.com/distribution/)

Note: You will need to quit and restart your command line terminal for your Anaconda installation to be enabled.

LandBOSSE doesn't support Python 2.x.

## Step 1a: Open the command prompt with the terminal

In finder, open the `Applications` folder and find the `Utilities` subfolder. Click on the `Terminal` app to start the command prompt.

## Step 1b: Create a folder structure

Somewhere on your computer create a directory structure for the LandBOSSE source code, input files and output files. For example if you want it on your desktop, from your terminal type the following:

``` 
mkdir ~/Desktop/landbosse
mkdir ~/Desktop/landbosse/input
mkdir ~/Desktop/landbosse/output
cd ~/Desktop/landbosse
```

You can put the folders somewhere else if you want. Just remember where they go when you use environment variables in this documentation. This directory structure will be referenced for all future commands in this document.

## Step 2: Fork and clone this repository

Forking and cloning are the two steps to installing the LandBOSSE code on your computer so you can you can run it.

### 2a. If you have forked and clone before, and use `git` on the command line.

1. Create your own fork of LandBOSSE under your own account.
1. Then clone with commands similar to `git clone https://github.com/YOUR USERNAME/LandBOSSE.git`. 

Now go to step 3.

### 2b. If you have NOT forked and/or cloned before, and want to use the command line, please read this.

1. Open your command prompt.
1. Install the `git` command line tool `xcode-select --install`
1. GitHub has some good documentation on learning about forking and cloning at [https://help.github.com/en/articles/fork-a-repo](https://help.github.com/en/articles/fork-a-repo)

After you've read the documentation, please return to [https://github.com/WISDEM/LandBOSSE](https://github.com/WISDEM/LandBOSSE). From there, fork the LandBOSSE repository and run the following commands:

```
cd ~/Desktop/landbosse
git clone https://github.com/YOUR USERNAME/LandBOSSE.git
cd LandBOSSE
```

Substitute `YOUR USERNAME` with the username or organization to which you forked your copy of LandBOSSE.

### 2c. If you use another tool other than command line `git`, follow these steps:

Using your software, make sure that you clone into the `cd ~/Desktop/landbosse` folder and follow the directions in this tutorial.

## Step 3: Set up a virtual environment
Setup a virtual environment for all your LandBOSSE dependencies.

```
conda create -n LandBOSSE python=3.7
conda activate LandBOSSE
```

All the commands in this README are meant to be executed within a virtual environment and within the `LandBOSSE` folder.

## Step 4: Install first set of packages

In order to run the code, modify the code, build the documentation and run the tests, you will neeed to install a few packages with conda. Type the following command to do so:

```
conda install pytest sphinx sphinx_rtd_theme
```

## Step 5: Install LandBOSSE itself, along with more packages

Install the package *for development* with the following command:

```
cd ~/Desktop/landbosse/LandBOSSE
pip install -e .
```

By installing it in developer mode with `pip` you have two benefits:

1. It can be uninstalled with `pip uninstall landbosse` (you don't need to uninstall it right now)
1. You can update the source code with re-installing the package because `pip` uses symbolic links (aka symlinks) to reference your source code directory.

## Step 6: Copy your input data

Copy the template file out to the `landbosse/input` directory that you created in Step 1. You should have a `projects_list.xlsx` file and a `project_data` subfolder in your input directory.

## Step 7: Environment variables

Because of the numerous files needed for execution of projects and the numerous timestamped output files, LandBOSSE uses environment variables to track folders where these files are stored. The following variables must be present in every execution of LandBOSSE

1. `LANDBOSSE_INPUT_DIR`: The absolute path to the folder containing `projects_list.xlsx` file and the `project_data` folder.
1. `LANDBOSSE_OUTPUT_DIR`: The absolute path to the folder where the output files will be placed.

If you want to find out more about environment variables in general, [you can optionally read about environment variables on Wikipedia](https://en.wikipedia.org/wiki/Environment_variable).

You can set these environment variables with:

1. `export LANDBOSSE_INPUT_DIR=???` and `export LANDBOSSE_OUTPUT_DIR=???` where `???` is where you need the environment variable to point.
1. In your `.bashrc` or `.zshrc` files
1. In your IDE, if you are a developer and use an IDE
1. On the same command line you execute LandBOSSE.

The first three are outside the scope of this document. The fourth, however, is how we will execute LandBOSSE in the next step.

## Step 8: Copy and modify template input files to input folder

In the `LandBOSSE` directory you will find a folder named `project_input_template`. Copy (do not move) the contents of this folder into the `inputs` folder you created and specified in Steps 3 and 7. Retain the folder structure in `project_input_template`.

The file named `projects_list.xlsx` must keep the same name. The names of the project data files in the `project_data` folder must match the project names in `projects_list.xlsx`.

## Step 9: Execute LandBOSSE

Suppose that you have created the directory structure on your desktop as mentioned above in step 2 "Create a folder structure". You can set the environment variables and execute LandBOSSE with a couple easy commands:

```
cd ~/Desktop/landbosse/LandBOSSE
python main.py -i ~/Desktop/landbosse/input -o ~/Desktop/landbosse/output 
```

The file will be produced with a filename like:

`landbosse-output-2019-6-18-13-8-2.xlsx`

Where the timestamp is in the format of *year-month-day-hour-minute-second*

## Step 10: Exiting your development environment
When you are done with your development work, type the following command:

```
conda deactivate
```

That will exit your virtual environment so that you can run other Python projects.

## *Developers step 11: Build documentation*
This step is for software developers.

You can automatically generate documentation from docstrings with Sphinx and autodoc. Whenever you update the `.rst` files or the docstrings in the `.py` files, you need to rebuild the documentation. From the `docs/` folder of this repository, run the following commands:

```
make clean
make html
```

After you run the command, you can open the documentation at:

```
docs/_build/html/index.html
```

## *Developers step 13: Run tests*
This step is for software developers.

LandBOSSE ships with a number of black box tests. These tests are intended to make sure that each module can execute without throwing exceptions.

To run these tests. change thw directory to the root of the repository. Ensure that your virtual environment is activated. Then, at the command prompt type the following command:

```
pytest
```

When all tests pass, output will be similar to the following:

```
============================ test session starts =============================
platform darwin -- Python 3.7.3, pytest-4.6.2, py-1.8.0, pluggy-0.12.0
rootdir: /XYZ/LandBOSSE
collected 29 items                                                           

landbosse/tests/model/test_CollectionCost.py .....                     [ 17%]
landbosse/tests/model/test_DevelopmentCost.py .                        [ 20%]
landbosse/tests/model/test_ErectionCost.py .                           [ 24%]
landbosse/tests/model/test_FoundationCost.py .                         [ 27%]
landbosse/tests/model/test_ManagementCost.py ...........               [ 65%]
landbosse/tests/model/test_RoadsCost.py .....                          [ 82%]
landbosse/tests/model/test_SubstationCost.py .                         [ 86%]
landbosse/tests/model/test_TransmissionCost.py .                       [ 89%]
landbosse/tests/model/test_WeatherDelay.py ...                         [100%]

========================= 29 passed in 8.63 seconds ==========================
```

Where `XYZ`, as shown above, will be substituted with the path to your LandBOSSE repository.

If there are failures, the resulting exceptions will be displayed for further inspection.
