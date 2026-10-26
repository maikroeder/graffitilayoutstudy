from zope.interface import Attribute, Interface


class IGraffitiPdfcheckLayer(Interface):
    """ Add-on browser layer (all views and viewlets register against this layer will appear on
    your Plone site only when the add-on installer has been run) """


class IPdfCheck(Interface):
    """ A check of a project, a `graffiti.pdfcheck.checks.Check`. Registered as a named utility, the name is the
    name of the check:

        <utility component=".pdfchecks.ONE_PAGE" provides="graffiti.pdfcheck.interfaces.IPdfCheck" name="one_page" />

    It runs in the check process without Zope: its module must not import Zope, its function must be defined at the
    top level of the module.
    """

    name = Attribute('The name of the check, also the name of the step in the result')
    tool = Attribute('The tool the check uses, for example pypdf')
    finding = Attribute('The finding when the function fails with an error')
    function = Attribute('Gets a graffiti.pdfcheck.checks.Context and returns a step')
    title = Attribute('The title on the settings page')


class IPdfCheckRunner(Interface):
    """ Runs the checks for one file. A project replaces this utility, for example to use an external service. """

    def check(path, settings):
        """ Checks the PDF file at `path` and returns the result as a dict like `graffiti.pdfcheck.checks.run_checks`.

        `settings` is a dict with the keys `checks`, `timeout`, `memory_mb`, `max_size_mb` and `programs`.
        `checks` are names, `graffiti.pdfcheck.settings.get_checks` returns the checks for them.
        """
