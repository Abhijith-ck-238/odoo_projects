from . import models
from . import controllers
from odoo.addons.payment import setup_provider, reset_payment_provider

def post_init_hook(env):
    setup_provider(env, 'cybropay')
    setup_provider(env, 'cybropay_direct')

def uninstall_hook(env):
    reset_payment_provider(env, 'cybropay')
    reset_payment_provider(env, 'cybropay_direct')
