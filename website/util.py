from flask import request

ALLOWED_LANGS = ['en', 'fr']

def preferred_language():
  langs = request.headers.get('Accept-Language', '').split(',')
  langs = [lang.strip() for lang in langs]
  langs = [lang.split(';')[0] for lang in langs]
  langs = [lang.strip() for lang in langs]
  for lang in langs:
    if len(lang) > 2:
      lang = lang[0:2]
    if lang in ALLOWED_LANGS:
      return lang
  return 'en'

