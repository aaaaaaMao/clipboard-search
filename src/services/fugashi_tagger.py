from fugashi import Tagger

tagger = Tagger('-Owakati')


def tag(text: str):
    result = []
    for word in tagger(text):
        result.append({
            'token': str(word),
            'lemma': word.feature.lemma,
            'orth': word.feature.orth,
            'pron': word.feature.pron,
            'orthBase': word.feature.orthBase,
            'pronBase': word.feature.pronBase,
            'cType': word.feature.cType,
            'cForm': word.feature.cForm,
            'lForm': word.feature.lForm,
            'pos': word.pos
        })
    return result
