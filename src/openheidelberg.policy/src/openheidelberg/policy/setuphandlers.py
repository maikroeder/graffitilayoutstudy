from interaktiv.framework.products import installer


def uninstall(context):
    """Uninstall script"""
    # Keep this list in sync with 'metadata.xml' of openheidelberg.policy
    uninstall_products = [
        'graffiti.policy',
        'openheidelberg.tile_card',

        'openheidelberg.policy',
    ]
    uninstall_products = list(set(uninstall_products) - {'openheidelberg.policy'})
    installer().uninstall_products(uninstall_products)
