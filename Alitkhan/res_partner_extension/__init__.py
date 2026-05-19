# -*- coding: utf-8 -*-

from . import controllers
from . import models


def post_init_hook(env):
    partners = env['res.partner'].search([])
    partners.compute_mixed_name()
