from odoo import models, fields, api

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'This is my Real Estate Property Type'
    _order = 'name'

    name = fields.Char(string="Name", required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    sequence = fields.Integer('Sequence', default=1)
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='Offers')
    offer_count = fields.Integer(compute='_compute_offer_count', string='Offer Count')

    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    # In estate_property_type.py
    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(name)', 'Type name must be unique.'),
    ]
