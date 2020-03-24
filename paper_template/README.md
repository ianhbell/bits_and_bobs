Some scripts and things for writing papers in LaTeX.

Recommendations:

* Have one master Python script (``make_figures.py``) for generating all figures, with the ability to comment out the calls to not generate a particular figure. Leave all the figures in the ``figs`` folder.  This guarantees that the figure formatting is applied to all figures consistently.
* Run the prepare_submission.py script to make a folder with all the files ready for submission to editorial system.
* At each stage of the submission pipeline, store the full set of files submitted to the journal, "0. initial submission", "1. revision 1", etc.  That way ``latexdiff`` can be used to build the diff between versions.
* When submitting, make sure to convert all PDF images to PDF/A (the submission script does this).  Otherwise the colors may shift in the journal PDF (been burned by that before).

Any questions: ian.bell@nist.gov