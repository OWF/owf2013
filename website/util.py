from flask import request

ALLOWED_LANGS = ['en', 'fr']

def preferred_language():
  langs = request.headers.get('Accept-Language', '').split(',')
  langs = [lang.strip() for lang in langs]
  langs = [lang.split(';')[0] for lang in langs]
  langs = [lang.strip() for lang in langs]
  for lang in ALLOWED_LANGS:
    if lang in langs:
      return lang
  return 'en'

