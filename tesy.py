import spacy
import data

nlp = spacy.load('en_core_web_sm', disable=['ner', 'textcat'])


def main():
    # Meeting to be processed
    text = data.getTestData("cr")
    i = 1
    services = []
    for t in text:
        sents = subjectverbobjectrule(t)
        if (len(sents) !=0):
            for sent in sents:
                services.append(sent)

    noDuplicateServices = removeDuplicates(services)

    for service in noDuplicateServices:
         print(i, " ", service)
         i += 1


def removeDuplicates(listwithdup):
    noduplist = []
    for i in listwithdup:
        if i not in noduplist:
            noduplist.append(i)
    return noduplist

def subjectverbobjectrule(text):
    doc = nlp(text)
    sent = []
    #print(doc)
    # displacy.render(doc, style='dep', jupyter=True)

    for token in doc:
        # if the token is a verb
        index = 0;
        if token.pos_ == 'VERB' or token.pos_ == 'AUX':
            phrase = token.text
            # only extract noun or pronoun subjects
            for subtok in token.rights:
                # save the object in the phrase
                if (subtok.dep_ in ['dobj','attr','prep']) and (subtok.pos_ in ['NOUN', 'PROPN','ADP']):
                    index = subtok.i
                    if adjectiveNounRule(text,index):
                        phrase += adjectiveNounRule(text,index) + ' ' + subtok.text
                    elif subtok.pos_ == 'ADP':
                        phrase = prepositionsRule(subtok.i,text)
                    else:
                        phrase += ' ' + subtok.text

                    for sub_tok in token.lefts:
                        if (sub_tok.dep_ in ['nsubj', 'nsubjpass']) and (sub_tok.pos_ in ['NOUN', 'PROPN', 'PRON']):
                            # add subject to the phrase
                            phrase = sub_tok.text + " " + phrase

                    sent.append(phrase)

    return sent


def adjectiveNounRule(text, index):
    doc = nlp(text)

    phrase = ''

    for token in doc:

        if token.i == index:
            for subtoken in token.children:
                if (subtoken.pos_ == 'ADJ'):
                    phrase += ' ' + subtoken.text
            break

    return phrase


def prepositionsRule(index,text):
    doc = nlp(text)
    token = doc[index]
    sent = []

    # look for prepositions
    phrase = ''

    # if its head word is a noun
    if token.head.pos_ in ['NOUN', 'PROPN','VERB']:

        # append noun and preposition to phrase
        phrase += token.head.text
        phrase += ' ' + token.text

        # check the nodes to the right of the preposition
        for right_tok in token.rights:
            # append if it is a noun or proper noun
            if (right_tok.dep_ == 'pobj'):
                phrase += ' ' + right_tok.text

        if len(phrase) > 2:
           return phrase



def rule0(text, index):
    doc = nlp(text)

    token = doc[index]

    entity = ''

    for sub_tok in token.children:
        if (sub_tok.dep_ in ['compound', 'amod']):
            entity += sub_tok.text + ' '

    entity += token.text

    return entity


def rule3_mod(token,text):
    phrase=""
    sent=[]
    if token.head.pos_ in ['NOUN', 'PROPN','VERB']:

        # appended rule
        append = rule0(text, token.head.i)
        if len(append) != 0:
            phrase += append
        else:
            phrase += token.head.text
            phrase += ' ' + token.text

        for right_tok in token.rights:
            if (right_tok.pos_ in ['NOUN', 'PROPN']):

                right_phrase = ''
                    # appended rule
                append = rule0(text, right_tok.i)
                if len(append) != 0:
                    right_phrase += ' ' + append
                else:
                    right_phrase += ' ' + right_tok.text

                    phrase += right_phrase

        if len(phrase) > 2:
            return phrase

    return phrase
main()
