from feincms.content.application.models import reverse

def get_redirect_url(url):
    """
    Tries to reverse url. If it doesn't work return the url itself.
    """
    try:
        return reverse(url)
    except:
        return url
