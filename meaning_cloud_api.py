import os
import requests

api_key = 'API-KEY'

def language_identification(text):
    url = "https://api.meaningcloud.com/lang-4.0/identification"

    payload={
        'key': api_key,
        'txt': text
    }

    response = requests.post(url, data=payload)

    json = response.json()

    table = [
        ['Language', 'Relevance'],
        [json['language_list'][0]['name'], json['language_list'][0]['relevance']]
    ]

    return(table)

def topic_extraction(lang, text):
    
    if lang == 'ENG':
        lang = 'en'
    elif lang == 'UKR':
        lang = 'uk'
    
    url = "https://api.meaningcloud.com/topics-2.0"
    
    payload={
        'key': api_key,
        'txt': text,
        'lang': lang,  
        'tt': 'ectmno' # named entities, concepts, time expressions,
    }

    response = requests.post(url, data=payload)
    
    json = response.json()
    
    table = [
        ['Entry Type', 'Relevance', 'Text', 'Type']
    ]
    
    for entity in json['entity_list']:
        en_type = str(entity['sementity']['type'])
        rf = en_type.rfind('>') 
        if rf >= 0:
            rf += 1
            en_type = en_type[rf:]
        table.append(['Entity', entity['relevance'], entity['form'], en_type])
    
    for concept in json['concept_list']:
        cn_type = str(concept['sementity']['type'])
        rf = cn_type.rfind('>') 
        if rf >= 0:
            rf += 1
            cn_type = cn_type[rf:]
        table.append(['Concept', concept['relevance'], concept['form'], cn_type])

    for time in json['time_expression_list']:
        table.append(['Time', '', time['form'], ''])

    for money in json['money_expression_list']:
        table.append(['Money', '', money['form'], ''])
    
    for quantity in json['quantity_expression_list']:
        table.append(['Quantity', '', quantity['form'], ''])
    
    for other in json['other_expression_list']:
        table.append(['Other', '', other['form'], ''])
    
    return(table)

def text_classification(model, lang, text):
    
    if lang == 'ENG':
        lang = 'en'
    elif lang == 'UKR':
        lang = 'uk'
        
    url = "https://api.meaningcloud.com/class-2.0"

    payload={
        'key': api_key,
        'txt': text,
        'model': f'{model}_{lang}',
    }

    response = requests.post(url, data=payload)

    json = response.json()
    
    table = [
        ['Label', 'Relevance', 'Absolute Relevance']
    ]
    
    for category in json['category_list']:
        table.append([category['label'], category['relevance'], category['abs_relevance']])

    return table

def summarization(text, num_of_sentences):

    url = "https://api.meaningcloud.com/summarization-1.0"

    payload={
        'key': api_key,
        'txt': text,
        'sentences': num_of_sentences
    }

    response = requests.post(url, data=payload)

    json = response.json()

    return json['summary']

def sentiment_analysis(lang, text):
    
    if lang == 'ENG':
        lang = 'en'
    elif lang == 'UKR':
        lang = 'uk'

    url = "https://api.meaningcloud.com/sentiment-2.1"

    payload={
        'key': api_key,
        'txt': text,
        'lang': lang,  # 2-letter code, like en es fr ...
    }

    response = requests.post(url, data=payload)

    json = response.json()
    
    table = [
        [json['summary']]
    ]

    return table

def corporate_reputation(lang, text):
    url = "https://api.meaningcloud.com/reputation-2.0"

    payload={
        'key': api_key,
        'txt': text,
        'lang': lang,
        'model': 'CorporateReputation'
    }

    response = requests.post(url, data=payload)

    print('Status code:', response.status_code)
    print(response.json())

def text_clustering(lang, text):
    url = "https://api.meaningcloud.com/clustering-1.1"

    payload={
        'key': api_key,
        'lang': lang,
        'txt': text
    }

    response = requests.post(url, data=payload)

    print('Status code:', response.status_code)
    print(response.json())

# topic_extraction('en', "In this example, we first import the Telegram modules and the dictionary script into the bot.py file. Next, we initialize the Telegram updater with our unique HTTP token.The start(update, context) function contains logic to render a custom welcome message when the bot’s /start command is run. We initiate a conversation with the user through the context.bot.send_message function, using chat_id to identify where to direct the response.")