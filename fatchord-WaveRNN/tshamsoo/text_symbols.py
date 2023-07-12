""" from https://github.com/keithito/tacotron """

'''
Defines the set of symbols used in text input to the model.
The default is a set of ASCII characters that works well for English or text
that has been run through Unidecode.
See TRAINING_DATA.md for details.
'''

_pad = '_'
_punctuation = r' -\.,;:?!"\'\(\)“”‘’~─'
_letters = sorted(set(
    'abcdefghijklmnopqrstuvwxyzáàâǎāa̍a̋éèêěēe̍e̋íìîǐīı̍i̍i̋'
    'óòôǒōo̍őó͘ò͘ô͘ǒ͘ō͘o̍͘ő͘úùûǔūu̍űḿm̀m̂m̌m̄m̍m̋ńǹn̂ňn̄n̍n̋ⁿ'
))
_tsong = _letters + list(''.join(_letters).upper())

_sooji = '0123456789'
_piantiau = '規本隨再固三仔海'

# Export all symbols:
symbols = (
    [_pad] + list(_punctuation)
    + list(_tsong) + list(_sooji) + list(_piantiau)
)
