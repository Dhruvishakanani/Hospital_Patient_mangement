from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Real Estate Property Tag'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer('Color')
    # In estate_property_tag.py
    _sql_constraints = [
        ('unique_tag_name', 'UNIQUE(name)', 'Tag name must be unique.'),
    ]