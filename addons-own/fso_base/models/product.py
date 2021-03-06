# -*- coding: utf-'8' "-*-"
from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fs_product_type = fields.Selection(selection=[('donation', 'Donation'),             # Spende
                                                  ('godparenthood', 'Godparenthood'),   # Patenschaft
                                                  ('sponsorship', 'Sponsorship'),       # Foerderer(schaft)
                                                  ('membership', 'Membership'),         # Mitgliedschaft
                                                  ('product', 'Product'),               # Produkt
                                                  ('eventticket', 'Event Ticket'),      # Event Ticket
                                                  ],
                                       string="Type")
