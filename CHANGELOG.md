# LandBOSSE Changelog

## 2.0.0 (August 1, 2019)

- Refactored into an object-oriented programming (OOP) architecture.
- Enable parallel computation of separate projects.
- Created an interface that takes inputs and outputs from and to `.xlsx` spreadsheets.
- Enhancements to all modules in model.
- Black box tests.
- Dictionary based interface to integrate with other modeling codes.

## 2.1.1 (October 9, 2019)

- In the `costs_by_module_type_operation` tab, standardize all costs to USD/kW per project, cost per project, cost per turbine.
- Improve docstrings in source code.
- Refactor more functionality into a new `CostModule` class.
- Clean up logging to use simple `print()` statements which are safe to use in multi-process parallel logging operations.

## 2.1.2 (October 24, 2019)

- Add separated "numeric value" and "non-numeric value" to columns on the details sheet.
- Add support to test current model output against previously known good model output to guard against regressions when the model is changed.
- Add support for command line options to control validation, input folder and output folder so that environment variables are not needed.
- Added documentation about command line operation with flowcharts about how LandBOSSE processes data according to the command line.
