# Copy this folder

Copy this folder and move it out of the git repo before you use it. Make sure you set the `LANDBOSSE_INPUT_DIR` to point to the location of this copy of the folder. Alternatively, you can use the `--input` or `-i` command line options to set the path to this input folder.

All the project files should have a name the matches the "Project ID" in `projects_list.xlsx` and should be placed in a `project_data` folder underneath the `projects_list.xlsx` file.

## Versions of `project_list.xlsx`

There are two version of `project_list.xlsx` in this folder. The first version is `project_list.xlsx`, which has all the inputs of LandBOSSE computed manually and is used for model validation. The second is `project_list_simplified.xlsx`, which has formulas for the home run trench length and project construction duration, each as a function of number of turbines.

In your custom inputs folder, make a copy of whichever spreadsheet best suits your needs. The second version may be easier to use for first-time users of LandBOSSE.
