import string


__all__ = ['source_markers', 'note_markers', 'method_markers', 'year_markers']


def source_markers():
    """ Returns the list of the source markers """
    values = [str(x) for x in range(1, 501)]
    return iter(values)


def note_markers():
    """ Returns the list of the note markers """
    values = string.ascii_lowercase + string.ascii_uppercase
    return iter(values)


def method_markers():
    """ Returns the list of the method markers """
    values = [
        '\\alpha', '\\beta', '\\gamma', '\\delta', '\\epsilon', '\\zeta',
        '\\eta', '\\theta', '\\iota', '\\kappa', '\\lambda', '\\mu', '\\nu',
        '\\omicron', '\\pi', '\\rho', '\\sigma', '\\tau', '\\upsilon', '\\phi',
        '\\chi', '\\psi', '\\omega', '\\Gamma', '\\Delta', '\\Theta',
        '\\Lambda', '\\Pi', '\\Sigma', '\\Upsilon', '\\Phi', '\\Psi', '\\Omega'
    ]
    return iter(values)


def year_markers():
    """ Returns the list of the year markers """
    values = [
        '\\Diamond', '\\triangle', '\\nabla', '\\S', '\\bigstar', '\\aleph',
        '\\infty', '\\Join', '\\natural', '\\mho', '\\emptyset', '\\partial',
        '\\textdollar', '\\triangleright', '\\triangleleft', '\\bullet',
        '\\star', '\\dagger', '\\ddagger', '\\oplus', '\\ominus', '\\otimes',
        '\\Box'
    ]
    return iter(values)
