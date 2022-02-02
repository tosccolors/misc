# -*- coding: utf-8 -*-
# Copyright 2016 Alex Comba <alex.comba@agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def post_init_hook(cr, registry):
    """
    This post-init-hook will update only product.product
    categ_id values in case they are not set
    """
    cr.execute(
        """
        UPDATE product_product
        SET categ_id = product_template.categ_id
        FROM product_template
        WHERE product_template.id = product_product.product_tmpl_id
        AND product_product.categ_id IS NULL
        """)
