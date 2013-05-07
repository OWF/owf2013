# coding=utf-8

"""
WTForms extensions (fields, widgets, validators).
"""

from jinja2 import Markup, escape
import operator
from sqlalchemy import UnicodeText
from flask import render_template
from flask.ext.babel import format_date
from wtforms import ValidationError, SelectMultipleField
from wtforms.compat import string_types, text_type

from wtforms.ext.sqlalchemy.fields import QuerySelectField, get_pk_from_identity, has_identity_key
from wtforms.fields import DateField, SelectFieldBase, SelectField
from wtforms.widgets import Select, Input, html_params


# TODO
SIRET = UnicodeText
PhoneNumber = UnicodeText
URL = UnicodeText
EmailAddress = UnicodeText


class SiretWidget(object):
  def render_view(self, field):
    siren = siret = unicode(field.object_data)
    if len(siret) > 9:
      siren = siret[:9]

    #FIXME: proper escape of siren required: risk of content injection
    url = u'http://societe.com/cgi-bin/recherche?rncs={}'.format(siren)
    return u'<a href="{url}">{siret}</a><i class="icon-share-alt"></i>'\
      .format(url=url, siret=siret)


class DateInput(Input):
  """
  Renders date inputs using the fancy Bootstrap Datepicker:
  http://www.eyecon.ro/bootstrap-datepicker/ .
  """
  input_type = 'date'

  def __call__(self, field, **kwargs):
    kwargs.setdefault('id', field.id)
    field_id = kwargs.pop('id')
    kwargs.pop('type', None)
    value = kwargs.pop('value', None)
    if value is None:
      value = field._value()
    if not value:
      value = ''
    format = field.format.replace("%", "")\
        .replace("d", "dd")\
        .replace("m", "mm")\
        .replace("Y", "yyyy")
    params = "data-date-format='%s' %s" % (
      format,
      html_params(name=field.name, id=field_id, value=value, **kwargs)
      )
    s = u'<div class="input-append date datepicker" %s>' \
        % html_params(**{'data-date': value, 'data-date-format': format})
    s += u'<input class="span2" size="13" type="text" %s>' \
        % html_params(name=field.name, id=field.id, value=value)
    s += u'<span class="add-on"><i class="icon-calendar"></i></span>'
    s += u'</div>'
    return Markup(s)

  def render_view(self, field):
    return format_date(field.object_data)


class DateField(DateField):
  """
  A text field which stores a `datetime.datetime` matching a format.
  """
  widget = DateInput()

  def __init__(self, label=None, validators=None, format='%d/%m/%Y', **kwargs):
    super(DateField, self).__init__(label, validators, format=format, **kwargs)
    self.format = format


#
# Selection widget and corresponding field.
#
class Select2(Select):
  """
  Transforms a Select widget into a Select2 widget. Depends on global JS code.
  """
  def __call__(self, *args, **kwargs):
    # Just add a select2 css class to the widget and let JQuery do the rest.
    kwargs = kwargs.copy()
    kwargs['class'] = 'select2'
    return Select.__call__(self, *args, **kwargs)

  def render_view(self, field, **kwargs):
    labels  = [label for v, label, checked in field.iter_choices() if checked]
    return u'; '.join(labels)


class Select2Ajax(object):
  """
  Ad-hoc select widget based on Select2.

  The code below is probably very fragile, since it depends on the internal
  structure of a Select2 widget.
  """
  def __init__(self, template='widgets/select2ajax.html'):
    self.template = template

  def __call__(self, field, **kwargs):
    css_class = kwargs.setdefault('class', u'')
    if 'js-widget' not in css_class:
      css_class += u' js-widget'
      kwargs['class'] = css_class

    extra_args = Markup(html_params(**kwargs))
    url = field.ajax_source
    object_name = field._data._name if field._data else ""
    object_id = field._data.id if field._data else ""

    return Markup(render_template(self.template,
                                  name=field.name,
                                  id=field.id,
                                  value=object_id, label=object_name, url=url,
                                  required=not field.allow_blank,
                                  extra_args=extra_args))


class QuerySelect2Field(SelectFieldBase):
  """
  COPY/PASTED (and patched) from WTForms!

  Will display a select drop-down field to choose between ORM results in a
  sqlalchemy `Query`.  The `data` property actually will store/keep an ORM
  model instance, not the ID. Submitting a choice which is not in the query
  will result in a validation error.

  This field only works for queries on models whose primary key column(s)
  have a consistent string representation. This means it mostly only works
  for those composed of string, unicode, and integer types. For the most
  part, the primary keys will be auto-detected from the model, alternately
  pass a one-argument callable to `get_pk` which can return a unique
  comparable key.

  The `query` property on the field can be set from within a view to assign
  a query per-instance to the field. If the property is not set, the
  `query_factory` callable passed to the field constructor will be called to
  obtain a query.

  Specify `get_label` to customize the label associated with each option. If
  a string, this is the name of an attribute on the model object to use as
  the label text. If a one-argument callable, this callable will be passed
  model instance and expected to return the label text. Otherwise, the model
  object's `__str__` or `__unicode__` will be used.

  If `allow_blank` is set to `True`, then a blank choice will be added to the
  top of the list. Selecting this choice will result in the `data` property
  being `None`. The label for this blank choice can be set by specifying the
  `blank_text` parameter.
  """
  # PATCHED!
  widget = Select2()

  def __init__(self, label=None, validators=None, query_factory=None,
               get_pk=None, get_label=None, allow_blank=False,
               blank_text='', **kwargs):
    super(QuerySelect2Field, self).__init__(label, validators, **kwargs)

    # PACTHED!
    if query_factory:
      self.query_factory = query_factory

    if get_pk is None:
      if not has_identity_key:
        raise Exception('The sqlalchemy identity_key function could not be imported.')
      self.get_pk = get_pk_from_identity
    else:
      self.get_pk = get_pk

    if get_label is None:
      self.get_label = lambda x: x
    elif isinstance(get_label, string_types):
      self.get_label = operator.attrgetter(get_label)
    else:
      self.get_label = get_label

    self.allow_blank = allow_blank
    self.blank_text = blank_text
    self.query = None
    self._object_list = None

  def _get_data(self):
    if self._formdata is not None:
      for pk, obj in self._get_object_list():
        if pk == self._formdata:
          self._set_data(obj)
          break
    return self._data

  def _set_data(self, data):
    self._data = data
    self._formdata = None

  data = property(_get_data, _set_data)

  def _get_object_list(self):
    if self._object_list is None:
      query = self.query or self.query_factory()
      get_pk = self.get_pk
      self._object_list = list((text_type(get_pk(obj)), obj) for obj in query)
    return self._object_list

  def iter_choices(self):
    if self.allow_blank:
      yield ('__None', self.blank_text, self.data is None)

    for pk, obj in self._get_object_list():
      yield (pk, self.get_label(obj), obj == self.data)

  def process_formdata(self, valuelist):
    if valuelist:
      if self.allow_blank and valuelist[0] == '__None':
        self.data = None
      else:
        self._data = None
        self._formdata = valuelist[0]

  def pre_validate(self, form):
    if not self.allow_blank or self.data is not None:
      for pk, obj in self._get_object_list():
        if self.data == obj:
          break
      else:
        raise ValidationError(self.gettext('Not a valid choice'))


class JsonSelect2Field(SelectFieldBase):
  """
  TODO: rewrite this docstring. This is copy-pasted from QuerySelectField

  Will display a select drop-down field to choose between ORM results in a
  sqlalchemy `Query`.  The `data` property actually will store/keep an ORM
  model instance, not the ID. Submitting a choice which is not in the query
  will result in a validation error.

  This field only works for queries on models whose primary key column(s)
  have a consistent string representation. This means it mostly only works
  for those composed of string, unicode, and integer types. For the most
  part, the primary keys will be auto-detected from the model, alternately
  pass a one-argument callable to `get_pk` which can return a unique
  comparable key.

  The `query` property on the field can be set from within a view to assign
  a query per-instance to the field. If the property is not set, the
  `query_factory` callable passed to the field constructor will be called to
  obtain a query.

  Specify `get_label` to customize the label associated with each option. If
  a string, this is the name of an attribute on the model object to use as
  the label text. If a one-argument callable, this callable will be passed
  model instance and expected to return the label text. Otherwise, the model
  object's `__str__` or `__unicode__` will be used.

  If `allow_blank` is set to `True`, then a blank choice will be added to the
  top of the list. Selecting this choice will result in the `data` property
  being `None`. The label for this blank choice can be set by specifying the
  `blank_text` parameter.
  """
  widget = Select2Ajax()

  def __init__(self, label=None, validators=None, ajax_source=None,
               blank_text='', model_class=None, **kwargs):
    super(JsonSelect2Field, self).__init__(label, validators, **kwargs)
    self.ajax_source = ajax_source
    self.model_class = model_class

    self.allow_blank = not self.is_required()
    self.blank_text = blank_text
    self._object_list = None

  # Another ad-hoc hack.
  def is_required(self):
    for validator in self.validators:
      rule = getattr(validator, "rule", {})
      if rule is not None and 'required' in rule:
        return True
    return False

  def _get_data(self):
    if self._formdata:
      id = int(self._formdata)
      obj = self.model_class.query.get(id)
      self._set_data(obj)
    return self._data

  def _set_data(self, data):
    self._data = data
    self._formdata = None

  data = property(_get_data, _set_data)

  def process_formdata(self, valuelist):
    if valuelist:
      if self.allow_blank and valuelist[0] == '':
        self.data = None
      else:
        self._data = None
        self._formdata = valuelist[0]

   # TODO really validate.
#  def pre_validate(self, form):
#    if not self.allow_blank or self.data is not None:
#      for pk, obj in self._get_object_list():
#        if self.data == obj:
#          break
#      else:
#        raise ValidationError(self.gettext('Not a valid choice'))

class Select2Field(SelectField):
  widget = Select2()

class Select2MultipleField(SelectMultipleField):
  widget = Select2(multiple=True)


COUNTRY_CHOICES = [
  ["FR", u"France"],
  ["AF", u"Afghanistan"],
  ["AX", u"Åland Islands"],
  ["AL", u"Albania"],
  ["DZ", u"Algeria"],
  ["AS", u"American Samoa"],
  ["AD", u"Andorra"],
  ["AO", u"Angola"],
  ["AI", u"Anguilla"],
  ["AQ", u"Antarctica"],
  ["AG", u"Antigua and Barbuda"],
  ["AR", u"Argentina"],
  ["AM", u"Armenia"],
  ["AW", u"Aruba"],
  ["AU", u"Australia"],
  ["AT", u"Austria"],
  ["AZ", u"Azerbaijan"],
  ["BS", u"Bahamas"],
  ["BH", u"Bahrain"],
  ["BD", u"Bangladesh"],
  ["BB", u"Barbados"],
  ["BY", u"Belarus"],
  ["BE", u"Belgium"],
  ["BZ", u"Belize"],
  ["BJ", u"Benin"],
  ["BM", u"Bermuda"],
  ["BT", u"Bhutan"],
  ["BO", u"Bolivia, Plurinational State of"],
  ["BQ", u"Bonaire, Sint Eustatius and Saba"],
  ["BA", u"Bosnia and Herzegovina"],
  ["BW", u"Botswana"],
  ["BV", u"Bouvet Island"],
  ["BR", u"Brazil"],
  ["IO", u"British Indian Ocean Territory"],
  ["BN", u"Brunei Darussalam"],
  ["BG", u"Bulgaria"],
  ["BF", u"Burkina Faso"],
  ["BI", u"Burundi"],
  ["KH", u"Cambodia"],
  ["CM", u"Cameroon"],
  ["CA", u"Canada"],
  ["CV", u"Cape Verde"],
  ["KY", u"Cayman Islands"],
  ["CF", u"Central African Republic"],
  ["TD", u"Chad"],
  ["CL", u"Chile"],
  ["CN", u"China"],
  ["CX", u"Christmas Island"],
  ["CC", u"Cocos (Keeling) Islands"],
  ["CO", u"Colombia"],
  ["KM", u"Comoros"],
  ["CG", u"Congo"],
  ["CD", u"Congo, the Democratic Republic of the"],
  ["CK", u"Cook Islands"],
  ["CR", u"Costa Rica"],
  ["CI", u"Côte d'Ivoire"],
  ["HR", u"Croatia"],
  ["CU", u"Cuba"],
  ["CW", u"Curaçao"],
  ["CY", u"Cyprus"],
  ["CZ", u"Czech Republic"],
  ["DK", u"Denmark"],
  ["DJ", u"Djibouti"],
  ["DM", u"Dominica"],
  ["DO", u"Dominican Republic"],
  ["EC", u"Ecuador"],
  ["EG", u"Egypt"],
  ["SV", u"El Salvador"],
  ["GQ", u"Equatorial Guinea"],
  ["ER", u"Eritrea"],
  ["EE", u"Estonia"],
  ["ET", u"Ethiopia"],
  ["FK", u"Falkland Islands (Malvinas)"],
  ["FO", u"Faroe Islands"],
  ["FJ", u"Fiji"],
  ["FI", u"Finland"],
  ["GF", u"French Guiana"],
  ["PF", u"French Polynesia"],
  ["TF", u"French Southern Territories"],
  ["GA", u"Gabon"],
  ["GM", u"Gambia"],
  ["GE", u"Georgia"],
  ["DE", u"Germany"],
  ["GH", u"Ghana"],
  ["GI", u"Gibraltar"],
  ["GR", u"Greece"],
  ["GL", u"Greenland"],
  ["GD", u"Grenada"],
  ["GP", u"Guadeloupe"],
  ["GU", u"Guam"],
  ["GT", u"Guatemala"],
  ["GG", u"Guernsey"],
  ["GN", u"Guinea"],
  ["GW", u"Guinea-Bissau"],
  ["GY", u"Guyana"],
  ["HT", u"Haiti"],
  ["HM", u"Heard Island and McDonald Islands"],
  ["VA", u"Holy See (Vatican City State)"],
  ["HN", u"Honduras"],
  ["HK", u"Hong Kong"],
  ["HU", u"Hungary"],
  ["IS", u"Iceland"],
  ["IN", u"India"],
  ["ID", u"Indonesia"],
  ["IR", u"Iran, Islamic Republic of"],
  ["IQ", u"Iraq"],
  ["IE", u"Ireland"],
  ["IM", u"Isle of Man"],
  ["IL", u"Israel"],
  ["IT", u"Italy"],
  ["JM", u"Jamaica"],
  ["JP", u"Japan"],
  ["JE", u"Jersey"],
  ["JO", u"Jordan"],
  ["KZ", u"Kazakhstan"],
  ["KE", u"Kenya"],
  ["KI", u"Kiribati"],
  ["KP", u"Korea, North"],
  ["KR", u"Korea, South"],
  ["KW", u"Kuwait"],
  ["KG", u"Kyrgyzstan"],
  ["LA", u"Lao People's Democratic Republic"],
  ["LV", u"Latvia"],
  ["LB", u"Lebanon"],
  ["LS", u"Lesotho"],
  ["LR", u"Liberia"],
  ["LY", u"Libya"],
  ["LI", u"Liechtenstein"],
  ["LT", u"Lithuania"],
  ["LU", u"Luxembourg"],
  ["MO", u"Macao"],
  ["MK", u"Macedonia, the former Yugoslav Republic of"],
  ["MG", u"Madagascar"],
  ["MW", u"Malawi"],
  ["MY", u"Malaysia"],
  ["MV", u"Maldives"],
  ["ML", u"Mali"],
  ["MT", u"Malta"],
  ["MH", u"Marshall Islands"],
  ["MQ", u"Martinique"],
  ["MR", u"Mauritania"],
  ["MU", u"Mauritius"],
  ["YT", u"Mayotte"],
  ["MX", u"Mexico"],
  ["FM", u"Micronesia, Federated States of"],
  ["MD", u"Moldova, Republic of"],
  ["MC", u"Monaco"],
  ["MN", u"Mongolia"],
  ["ME", u"Montenegro"],
  ["MS", u"Montserrat"],
  ["MA", u"Morocco"],
  ["MZ", u"Mozambique"],
  ["MM", u"Myanmar"],
  ["NA", u"Namibia"],
  ["NR", u"Nauru"],
  ["NP", u"Nepal"],
  ["NL", u"Netherlands"],
  ["NC", u"New Caledonia"],
  ["NZ", u"New Zealand"],
  ["NI", u"Nicaragua"],
  ["NE", u"Niger"],
  ["NG", u"Nigeria"],
  ["NU", u"Niue"],
  ["NF", u"Norfolk Island"],
  ["MP", u"Northern Mariana Islands"],
  ["NO", u"Norway"],
  ["OM", u"Oman"],
  ["PK", u"Pakistan"],
  ["PW", u"Palau"],
  ["PS", u"Palestinian Territory, Occupied"],
  ["PA", u"Panama"],
  ["PG", u"Papua New Guinea"],
  ["PY", u"Paraguay"],
  ["PE", u"Peru"],
  ["PH", u"Philippines"],
  ["PN", u"Pitcairn"],
  ["PL", u"Poland"],
  ["PT", u"Portugal"],
  ["PR", u"Puerto Rico"],
  ["QA", u"Qatar"],
  ["RE", u"Réunion"],
  ["RO", u"Romania"],
  ["RU", u"Russian Federation"],
  ["RW", u"Rwanda"],
  ["BL", u"Saint Barthélemy"],
  ["SH", u"Saint Helena, Ascension and Tristan da Cunha"],
  ["KN", u"Saint Kitts and Nevis"],
  ["LC", u"Saint Lucia"],
  ["MF", u"Saint Martin (French part)"],
  ["PM", u"Saint Pierre and Miquelon"],
  ["VC", u"Saint Vincent and the Grenadines"],
  ["WS", u"Samoa"],
  ["SM", u"San Marino"],
  ["ST", u"Sao Tome and Principe"],
  ["SA", u"Saudi Arabia"],
  ["SN", u"Senegal"],
  ["RS", u"Serbia"],
  ["SC", u"Seychelles"],
  ["SL", u"Sierra Leone"],
  ["SG", u"Singapore"],
  ["SX", u"Sint Maarten (Dutch part)"],
  ["SK", u"Slovakia"],
  ["SI", u"Slovenia"],
  ["SB", u"Solomon Islands"],
  ["SO", u"Somalia"],
  ["ZA", u"South Africa"],
  ["GS", u"South Georgia and the South Sandwich Islands"],
  ["SS", u"South Sudan"],
  ["ES", u"Spain"],
  ["LK", u"Sri Lanka"],
  ["SD", u"Sudan"],
  ["SR", u"Suriname"],
  ["SJ", u"Svalbard and Jan Mayen"],
  ["SZ", u"Swaziland"],
  ["SE", u"Sweden"],
  ["CH", u"Switzerland"],
  ["SY", u"Syrian Arab Republic"],
  ["TW", u"Taiwan, Province of China"],
  ["TJ", u"Tajikistan"],
  ["TZ", u"Tanzania, United Republic of"],
  ["TH", u"Thailand"],
  ["TL", u"Timor-Leste"],
  ["TG", u"Togo"],
  ["TK", u"Tokelau"],
  ["TO", u"Tonga"],
  ["TT", u"Trinidad and Tobago"],
  ["TN", u"Tunisia"],
  ["TR", u"Turkey"],
  ["TM", u"Turkmenistan"],
  ["TC", u"Turks and Caicos Islands"],
  ["TV", u"Tuvalu"],
  ["UG", u"Uganda"],
  ["UA", u"Ukraine"],
  ["AE", u"United Arab Emirates"],
  ["GB", u"United Kingdom"],
  ["US", u"United States"],
  ["UM", u"United States Minor Outlying Islands"],
  ["UY", u"Uruguay"],
  ["UZ", u"Uzbekistan"],
  ["VU", u"Vanuatu"],
  ["VE", u"Venezuela, Bolivarian Republic of"],
  ["VN", u"Viet Nam"],
  ["VG", u"Virgin Islands, British"],
  ["VI", u"Virgin Islands, U.S."],
  ["WF", u"Wallis and Futuna"],
  ["EH", u"Western Sahara"],
  ["YE", u"Yemen"],
  ["ZM", u"Zambia"],
  ["ZW", u"Zimbabwe"],
]

def all_countries():
  # XXX: Empty option is currently hardcoded.
  return [["", u""]] + COUNTRY_CHOICES
