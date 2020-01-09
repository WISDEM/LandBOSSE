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

## 2.1.3 (October 29, 2019)

- Removed an empty and unimplemented function from `DefaultMasterInputDict.py`.

## 2.1.4 (November 1, 2019)

- Enhanced `.xlsx` input performance for faster execution time.

## 2.1.5 (November 8, 2019)

- Added outputs for erection crew cost, wind multiplier and mobilization of each process of the erection to the details output sheet.

## 2.2.0 (November 24, 2019)

- Support for parametric variable grid search added.

## 2.2.1 (December 12, 2019)

+ Support for discrete value lists for parameteric variables added.

+ Support for labor rate multipliers added.

## 2.2.2 (December 13, 2019)

+ Added support for crane breakdowns

+ Fixed a roads issue.
