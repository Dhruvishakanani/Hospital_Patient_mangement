from asyncio import exceptions

from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero
from reportlab.graphics.transform import inverse

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "This is real estate property. I will make to try this."
    _order = 'id desc'

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Date Availability", default=lambda self: fields.Date.today() + timedelta(days=90), copy=False)
    expected_price = fields.Float(string="Expected Price")
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Float(string="Living Area (sqm)")
    garden_area = fields.Float(string="Garden Area (sqm)")
    total_area = fields.Float(string="Total Area (sqm)",compute='_compute_total_area', store=True)
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('south', 'South'), ('east', 'East'), ('west', 'West'), ('north', 'North')],
        help="Type is used to separate Leads and Opportunities")
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled')
    ],
        default='new', required=True)
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string='Buyer')
    salesperson_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
    offer_ids = fields.One2many('estate.property.offer', inverse_name='property_id', string='Offers')
    best_price = fields.Float(string="Best Offer",compute='_compute_best_price', store=True)

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for prop in self:
            prop.total_area = prop.living_area + prop.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for prop in self:
            if prop.offer_ids:
                prop.best_price = max(prop.offer_ids.mapped('price'))
            else:
                prop.best_price = 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_cancel(self):
        for prop in self:
            if prop.state == 'sold':
                raise UserError("Sold properties cannot be canceled.")
            prop.state = 'canceled'
        return True

    def action_sold(self):
        if self.state == 'canceled':
            raise UserError("Canceled properties cannot be sold.")
        if not self.buyer_id:
            raise UserError("Cannot sell a property without a buyer. Please accept an offer first.")
        self.state = 'sold'

        return self

    _sql_constraints = [
        ('expected_price_positive', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive!'),
    ]

    @api.constrains('expected_price')
    def expected_price_positive(self):
        for record in self:
            if record.expected_price <= 0:
                raise ValidationError('Expected price must be strictly positive.')

    @api.ondelete(at_uninstall=False)
    def _check_state_before_deletion(self):
        for property in self:
            if property.state not in ['new', 'cancelled']:
                raise models.ValidationError("You cannot delete a property that is not new or cancelled.")
