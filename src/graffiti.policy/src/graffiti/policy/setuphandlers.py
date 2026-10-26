import plone.api as api
from interaktiv.framework.products import installer


def create_cronjob_user():
    cron_admin = api.user.get(username='cron_admin')
    if not cron_admin:
        cron_admin = api.user.create(username='cron_admin', email='cron_admin@plone-testuser.test')
        cron_admin.setMemberProperties(mapping={'fullname': 'Cronjob Admin'})
        api.user.grant_roles(user=cron_admin, roles=['Manager'])


def post_install(context):
    create_cronjob_user()


def uninstall(context):
    """Uninstall script"""
    # Keep this list in sync with 'metadata.xml' of graffiti.policy
    uninstall_products = [
        'interaktiv.framework',
        'interaktiv.layout',
        'interaktiv.fonts',
        'interaktiv.image_focus',
        'interaktiv.migrator',
        'interaktiv.workingcopy',

        'interaktiv.basetiles',
        'interaktiv.tile_image',
        'interaktiv.tile_text',
        'interaktiv.tile_files',
        'interaktiv.tile_subheadline',
        'interaktiv.tile_news',
        'interaktiv.tile_audio',
        'interaktiv.tile_button',
        'interaktiv.tile_collapse',
        'interaktiv.tile_contact',
        'interaktiv.tile_icon',
        'interaktiv.tile_iframe',
        'interaktiv.tile_line',
        'interaktiv.tile_map',
        'interaktiv.tile_slider',
        'interaktiv.tile_spacer',
        'interaktiv.tile_timeline',
        'interaktiv.tile_video',
        'interaktiv.tilepage_versioning',
        'interaktiv.theme',

        'graffiti.policy',
        'graffiti.contenttypes',
        'graffiti.tile_listing',
        'graffiti.tile_search',
        'graffiti.tile_dashboard',
        'graffiti.tile_tabs',
        'graffiti.tile_view',
        'graffiti.tile_button',
        'graffiti.pdfcheck',
    ]
    uninstall_products = list(set(uninstall_products) - {'graffiti.policy'})
    installer().uninstall_products(uninstall_products)
