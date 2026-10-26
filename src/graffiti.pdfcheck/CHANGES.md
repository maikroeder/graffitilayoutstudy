# Changes

New versions go on top.

## 1.0.0 (unreleased)

- The checks for one PDF file in plain Python: header, open, text, rewrite with metadata, pdfunite, qpdf. #22774
- Hints besides findings: qpdf warnings, and what rebuilding or appending loses (bookmarks, form fields, signatures, embedded files). Hints do not make a file unsuitable. #22774
- `check_pdf` runs the checks in their own process with a time and a memory limit, larger files than the size limit are not checked. #22774
- Projects register their own checks as named utilities `IPdfCheck`, with a title and sentences for editors, and replace the utility `IPdfCheckRunner`, for example with an external service. #22774
- Check on upload of the content type File: result as an annotation, status message, viewlet for editors, API and view `@@pdfcheck` for workflow guards. #22774
- Settings in the registry and the page "PDF check settings", German translations. #22774
- Sample files for the tests, made in code. #22774
- Result in the view of the file: one box beside a floating preview image, findings and hints as whole sentences, the parts that get lost in one sentence, what the programs say under "Technical details". #22774
- Settings page: the built-in checks and the registered checks of projects as check boxes with readable names, for developers with the name and the function of each check, clearer help texts. #22774
- The paths of pdfunite and qpdf and the Python of the check process come from environment variables, not from the settings page: whoever may change the settings must not start programs on the server. #22774
- A check that could not finish is repeated for the same file, a result without any check that ran is "not checked", a result of an older file is removed when no check runs, files over the size limit are not read. #22774
- The check process gets no input, its result lines carry a marker, it is not waited for without limit after the time limit, a stop before the first check is "not checked". #22774
- Subscribers, viewlets, control panels, widgets, utilities, vocabularies and the registry schema in folders of their own; `check_object` is now `graffiti.pdfcheck.api.check_object`. #22774
