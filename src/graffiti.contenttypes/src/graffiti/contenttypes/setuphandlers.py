from interaktiv.framework.products import installer


def post_install(context):
    pass

def uninstall(context):
    """Uninstall script"""
    # Keep this list in sync with 'metadata.xml' of graffiti.contenttypes
    uninstall_products = [
        'graffiti.contenttypes'
    ]
    uninstall_products = list(set(uninstall_products) - {'graffiti.contenttypes'})
    installer().uninstall_products(uninstall_products)
