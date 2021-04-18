import requests
import urllib3
import csv
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.exceptions import ConnectionError, ReadTimeout
from bs4 import BeautifulSoup

from google.cloud import language_v1 as language

from google.api_core.exceptions import InvalidArgument
import six
import sys
import re

# User indicates upload method
print('-' * 20)
print('Running bulk URLs? (bulk)')
print('Uploading content directly? (direct)')
print('')
decision = input('Enter upload type: ')

TIMEOUT = 30

# # FILES TO USE (Win)
# DIRECT_A_FILE = '.\DIRECT.txt'
# DIRECT_B_FILE = '.\DIRECT.txt'
# DIRECT_C_FILE = '.\DIRECT.txt'
# DIRECT_D_FILE = '.\DIRECT.txt'
# DIRECT_E_FILE = '.\DIRECT.txt'
#
# BULK_A_FILE = '.\gnl-bulk-check.txt'
# BULK_B_FILE = '.\gnl-bulk-check.txt'
# BULK_C_FILE = '.\gnl-bulk-check.txt'
# BULK_D_FILE = '.\gnl-bulk-check.txt'

# FILES TO USE (Unix)
DIRECT_A_FILE = './DIRECT.txt'
DIRECT_B_FILE = './DIRECT.txt'
DIRECT_C_FILE = './DIRECT.txt'
DIRECT_D_FILE = './DIRECT.txt'
DIRECT_E_FILE = './DIRECT.txt'

BULK_A_FILE = './gnl-bulk-check.txt'
BULK_B_FILE = './gnl-bulk-check.txt'
BULK_C_FILE = './gnl-bulk-check.txt'
BULK_D_FILE = './gnl-bulk-check.txt'

# Handles content entered directly into .txt file
if decision == 'direct':
    while True:
        print('-' * 20)
        print('Choose an analysis to run:')
        print('')
        print('Run Sentiment Analysis? (A)')
        print('Run Content Classification? (B)')
        print('Run Entities Analysis? (C)')
        print('Run Entity Sentiment Analysis? (D)')
        print('Run Syntax Analysis? (E)')
        print('-' * 20)
        print('')

        # Each analysis will correspond with a letter from the list above.
        choice = input('Which Analysis to Run? ')

        # Content Classification (gnl-classify.content.py)
        if choice == 'B' or choice == 'b':

            with open(DIRECT_B_FILE, 'r', encoding="utf8") as gnl:

                content = gnl.read()
                content = str(content)

                downloadFile = 'gnl-content-direct.csv'
                with open(downloadFile, 'w') as file:
                    filewriter = csv.writer(file)

                    columnHead = 'String,Type,Confidence'
                    filewriter.writerow(columnHead.split(','))


                    def classify_text(text):

                        client = language.LanguageServiceClient()

                        if isinstance(text, six.binary_type):
                            text = text.decode('utf-8')

                        document = language.Document(content=text.encode('utf-8'),
                                                     type_=language.Document.Type.PLAIN_TEXT)

                        categories = client.classify_text(document=document).categories

                        for category in categories:
                            print(u'{:<16}: {}'.format('type', category.name))
                            print(u'{:<16}: {}'.format(
                                'confidence', category.confidence))
                            print(u'{:<16}: {}'.format('content', content) + '\n')
                            print('')

                            row = [content, category.name, category.confidence]
                            filewriter.writerow(row)

                    try:
                        classify_text(content)
                    except InvalidArgument as e:
                        print(f'{e}')

        # Sentiment Analysis (google-natural-language-api.py)
        if choice == 'A' or choice == 'a':
            with open(DIRECT_A_FILE, 'r', encoding="utf8") as gnl:
                downloadFile = 'gnl-sentiment-direct.csv'
                with open(downloadFile, 'w') as file:
                    filewriter = csv.writer(file)
                    content2 = gnl.read()

                    columnHead = 'Content,Sentiment Score,Sentiment Magnitude'
                    filewriter.writerow(columnHead.split(','))

                    # Instantiates a client
                    client = language.LanguageServiceClient()

                    doc = language.Document
                    document = language.Document(content=content2,
                                                 type_=language.Document.Type.PLAIN_TEXT)

                    # Detects the sentiment of the text
                    sentiment = client.analyze_sentiment(document=document).document_sentiment

                    print('Content: {}'.format(content2))
                    print('Sentiment: {}, {}'.format(
                        sentiment.score, sentiment.magnitude))

                    row = [content2, sentiment.score, sentiment.magnitude]
                    filewriter.writerow(row)

        # Entity Sentiment (gnl-entity-sentiment.py)
        if choice == 'D' or choice == 'd':
            with open(DIRECT_D_FILE, 'r', encoding="utf8") as gnl:
                downloadFile = 'gnl-entity-sent-direct.csv'
                with open(downloadFile, 'w') as file:
                    filewriter = csv.writer(file)
                    content3 = gnl.read()

                    columnHead = 'Name,Begin Offset,Content,Magnitude,Sentiment,Type,Salience,Sentiment'
                    filewriter.writerow(columnHead.split(','))


                    def entity_sentiment_text(text):
                        """Detects entity sentiment in the provided text."""
                        client = language.LanguageServiceClient()

                        if isinstance(text, six.binary_type):
                            text = text.decode('utf-8')

                        document = language.Document(content=text.encode('utf-8'),
                                                     type_=language.Document.Type.PLAIN_TEXT)

                        #  Detect and send native Python encoding to receive correct word offsets.
                        encoding = language.EncodingType.UTF32
                        if sys.maxunicode == 65535:
                            encoding = language.EncodingType.UTF16

                        result = client.analyze_entity_sentiment(document=document, encoding_type=encoding)

                        for entity in result.entities:
                            print('Mentions: ')
                            print(u'Name: "{}"'.format(entity.name))
                            for mention in entity.mentions:
                                print(u'  Begin Offset : {}'.format(
                                    mention.text.begin_offset))
                                print(u'  Content : {}'.format(mention.text.content))
                                print(u'  Magnitude : {}'.format(
                                    mention.sentiment.magnitude))
                                print(u'  Sentiment : {}'.format(
                                    mention.sentiment.score))
                                print(u'  Type : {}'.format(mention.type_))
                                print(u'Salience: {}'.format(entity.salience))
                                print(u'Sentiment: {}\n'.format(entity.sentiment))

                                row = [entity.name, mention.text.begin_offset, mention.text.content,
                                       mention.sentiment.magnitude, mention.sentiment.score, mention.type_,
                                       entity.salience, entity.sentiment]
                                filewriter.writerow(row)

                    entity_sentiment_text(content3)

        # Entity Analysis (gnl-entities.py)
        if choice == 'C' or choice == 'c':
            with open(DIRECT_C_FILE, 'r', encoding="utf8") as gnl:
                downloadFile = 'gnl-entity-analysis-direct.csv'
                with open(downloadFile, 'w') as file:
                    filewriter = csv.writer(file)
                    content4 = gnl.read()
                    columnHead = 'Name,Type,Salience,Wikipedia URL,MID'
                    filewriter.writerow(columnHead.split(','))

                    client = language.LanguageServiceClient()

                    if isinstance(content4, six.binary_type):
                        content4 = content4.decode('utf-8')

                    # Instantiates a plain text document.
                    document = language.Document(content=content4,
                                                 type_=language.Document.Type.PLAIN_TEXT)

                    # Detects entities in the document. You can also analyze HTML with:
                    # Document.type == language.Document.Type.HTML
                    entities = client.analyze_entities(document=document).entities

                    for entity in entities:
                        entity_type = language.Entity.Type(entity.type_)
                        print('=' * 20)
                        print(u'{:<16}: {}'.format('name', entity.name))
                        print(u'{:<16}: {}'.format('type', entity_type.name))
                        print(u'{:<16}: {}'.format('salience', entity.salience))
                        print(u'{:<16}: {}'.format('wikipedia_url', entity.metadata.get('wikipedia_url', '-')))
                        print(u'{:<16}: {}'.format('mid', entity.metadata.get('mid', '-')))

                        row = [entity.name, entity_type.name, entity.salience,
                               entity.metadata.get("wikipedia_url"), entity.metadata.get("mid")]
                        filewriter.writerow(row)

        # Syntax Analysis (gnl-analyze-syntax.py)
        if choice == 'E' or choice == 'e':
            with open(DIRECT_E_FILE, 'r', encoding="utf8") as gnl:
                downloadFile = 'gnl-syntax-analysis.csv'
                with open(downloadFile, 'w') as file:
                    filewriter = csv.writer(file)
                    content5 = gnl.read()

                    columnHead = 'POS Tag,Content'
                    filewriter.writerow(columnHead.split(','))


                    def syntax_text(text):
                        """Detects syntax in the text."""
                        client = language.LanguageServiceClient()

                        if isinstance(text, six.binary_type):
                            text = text.decode('utf-8')

                        # Instantiates a plain text document.
                        document = language.Document(content=text,
                                                     type_=language.Document.Type.PLAIN_TEXT)

                        # Detects syntax in the document. You can also analyze HTML with:
                        #   document.type == language.Document.Type.HTML
                        tokens = client.analyze_syntax(document=document).tokens

                        # part-of-speech tags from enums.PartOfSpeech.Tag
                        pos_tag = ('UNKNOWN', 'ADJ', 'ADP', 'ADV', 'CONJ', 'DET', 'NOUN', 'NUM', 'PRON', 'PRT', 'PUNCT',
                                   'VERB', 'X', 'AFFIX')

                        for token in tokens:
                            print(u'{}: {}'.format(pos_tag[token.part_of_speech.tag], token.text.content))
                            row = [pos_tag[token.part_of_speech.tag], token.text.content]
                            filewriter.writerow(row)

                    syntax_text(content5)

        # This if statement handles if while loop continues or breaks based on user input
        decision = input('Run another analysis? (Y/N) ')
        if decision == 'N' or decision == 'n':
            break

    # ---- Handles bulk URL check ----
if decision == 'bulk':
    while True:
        print('-' * 20)
        print('Choose an analysis to run:')
        print('')
        print('Run Sentiment Analysis? (A)')
        print('Run Content Classification? (B)')
        print('Run Entities Analysis? (C)')
        print('Run Entity Sentiment Analysis? (D)')
        print('-' * 20)
        print('')

        # Each analysis will correspond with a letter from the list above.
        choice = input('Which Analysis to Run? ')

        # Content Classification (gnl-classify.content.py)
        if choice == 'B' or choice == 'b':
            tagTarget = input('Target which tag type? (E.g. p, div): ')  # Allows user to select which tags to target

            filedownload = 'gnl-content-bulk.csv'
            with open(filedownload, "w") as file:
                filewriter = csv.writer(file)

                columnHead = 'URL,Type,Confidence,Content'
                filewriter.writerow(columnHead.split(','))


                def classify_text(text):

                    """Classifies content categories of the provided text."""
                    client = language.LanguageServiceClient()

                    if isinstance(text, six.binary_type):
                        text = text.decode('utf-8')

                    document = language.Document(content=text.encode('utf-8'),
                                                 type_=language.Document.Type.PLAIN_TEXT)

                    categories = client.classify_text(document=document).categories

                    for category in categories:
                        print(u'=' * 20)
                        print(u'{:<16}: {}'.format('url', url))
                        print(u'{:<16}: {}'.format('type', category.name))
                        print(u'{:<16}: {}'.format('confidence', category.confidence))
                        # print(u'{:<16}: {}'.format('string', data) + '\n')

                        row = [url, category.name, category.confidence, text]
                        filewriter.writerow(row)


                with open(BULK_B_FILE, 'r', encoding="utf8") as b:
                    content = b.readlines()
                    content = [line.rstrip('\n') for line in content]
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML,'
                                             ' like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

                    for url in content:
                        try:
                            # https://stackoverflow.com/questions/17782142/why-doesnt-requests-get-return-what-is-the-default-timeout-that-requests-get
                            html = requests.get(url, headers=headers, verify=False, timeout=TIMEOUT)
                        except ConnectionError as e:
                            print(f'{e} ~ {url}')
                            continue
                        except ReadTimeout as e1:
                            print(f'{e1} ~ {url}')
                            continue

                        bs = BeautifulSoup(html.text, 'html.parser')

                        content = bs.find_all(tagTarget)  # Finds all content within <html> tags and saves to variable

                        tagRemoval = re.compile(r'<[^>]+>')  # This regex removes all text between and including HTML tags


                        def remove_tags(text):  # This is the function called with the text to be stripped of HTML tags
                            final = tagRemoval.sub('', text)
                            print(final)
                            classify_text(final)

                        content = str(content)
                        try:
                            remove_tags(content)
                        except InvalidArgument as e:
                            pass

        # Sentiment Analysis (google-natural-language-api.py)
        if choice == 'A' or choice == 'a':

            with open(BULK_A_FILE, 'r', encoding="utf8") as b:
                downloadFile = 'gnl-sentiment-bulk.csv'
                with open(downloadFile, "w") as file:
                    filewriter = csv.writer(file)

                    columnHead = 'URL,Sentiment'
                    filewriter.writerow(columnHead.split(","))

                    content = b.readlines()
                    content = [line.rstrip('\n') for line in content]
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML,'
                                      ' like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    for url in content:

                        try:
                            html = requests.get(url, headers=headers, verify=False)

                        except ConnectionError as e:

                            print(f'{e} ~ {url}')

                        bs = BeautifulSoup(html.text, 'html.parser')

                        content = bs.find_all('p')
                        content = str(content)

                        # Instantiates a client
                        client = language.LanguageServiceClient()

                        document = language.Document(content=content,
                                                     type_=language.Document.Type.PLAIN_TEXT)

                        # Detects the sentiment of the text
                        sentiment = client.analyze_sentiment(document=document).document_sentiment

                        print('URL~ {}'.format(url))
                        print('Sentiment: {}, {}'.format(
                            sentiment.score, sentiment.magnitude) + '\n')
                        print('')

                        row = [url, sentiment.magnitude]
                        filewriter.writerow(row)

        # Entity Sentiment (gnl-entity-sentiment.py)
        if choice == 'D' or choice == 'd':
            downloadFile = 'gnl-entity-sent-bulk.csv'
            with open(downloadFile, 'w') as file:
                filewriter = csv.writer(file, quoting=csv.QUOTE_MINIMAL, )

                columnHead = 'URL,Name,Begin Offset,Content,Magnitude,Sentiment,Type,Salience,Entity Sentiment'
                filewriter.writerow(columnHead.split(','))


                def entity_sentiment_text(text):

                    """Detects entity sentiment in the provided text."""
                    client = language.LanguageServiceClient()

                    if isinstance(text, six.binary_type):
                        text = text.decode('utf-8')

                    document = language.Document(content=text.encode('utf-8'),
                                                 type_=language.Document.Type.PLAIN_TEXT)

                    #  Detect and send native Python encoding to receive correct word offsets.
                    encoding = language.EncodingType.UTF32
                    if sys.maxunicode == 65535:
                        encoding = language.EncodingType.UTF16

                    result = client.analyze_entity_sentiment(document=document, encoding_type=encoding)

                    for entity in result.entities:
                        print('Mentions: ')
                        print(u'URL ~ "{}'.format(url))
                        print(u'Name: "{}"'.format(entity.name))
                        for mention in entity.mentions:
                            print(u'  Begin Offset : {}'.format(
                                mention.text.begin_offset))
                            print(u'  Content : {}'.format(mention.text.content))
                            print(u'  Magnitude : {}'.format(
                                mention.sentiment.magnitude))
                            print(u'  Sentiment : {}'.format(
                                mention.sentiment.score))
                            print(u'  Type : {}'.format(mention.type_))
                            print(u'Salience: {}'.format(entity.salience))
                            print(u'Sentiment: {}\n'.format(entity.sentiment))

                            row2 = [url, entity.name, mention.text.begin_offset, mention.text.content,
                                    mention.sentiment.magnitude, entity.sentiment, mention.type_, entity.salience, entity.sentiment]
                            filewriter.writerow(row2)


                with open(BULK_D_FILE, 'r', encoding="utf8") as b:
                    content = b.readlines()
                    content = [line.rstrip('\n') for line in content]
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML,'
                                      ' like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

                    for url in content:
                        try:
                            html = requests.get(url, headers=headers, verify=False)
                        except ConnectionError as e:
                            print(f'{e} ~ {url}')

                        bs = BeautifulSoup(html.text, 'html.parser')
                        content = bs.find_all('p')

                        try:
                            for data in content:
                                entity_sentiment_text(data)
                        except InvalidArgument as e:
                            print(f'{e} ~ {url}')

        # Entity Analysis (gnl-entities.py)
        if choice == 'C' or choice == 'c':
            with open(BULK_C_FILE, 'r', encoding="utf8") as b:

                downloadFile = 'gnl-entity-bulk.csv'
                with open(downloadFile, 'w') as file:
                    filewriter = csv.writer(file)

                    columnHead = 'URL,Name,Type,Salience,Wikipedia URL,MID'
                    filewriter.writerow(columnHead.split(','))

                    content = b.readlines()
                    content = [line.rstrip('\n') for line in content]
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML,'
                                             ' like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    for url in content:

                        try:
                            html = requests.get(url, headers=headers, verify=False)

                        except ConnectionError as e:

                            print(f'{e} ~ {url}')

                        bs = BeautifulSoup(html.text, 'html.parser')

                        content = bs.find_all('p')
                        content = str(content)

                        client = language.LanguageServiceClient()

                        if isinstance(content, six.binary_type):
                            content = content.decode('utf-8')

                        # Instantiates a plain text document.
                        document = language.Document(content=content,
                                                     type_=language.Document.Type.PLAIN_TEXT)

                        # Detects entities in the document. You can also analyze HTML with:
                        # Document.type == language.Document.Type.HTML
                        entities = client.analyze_entities(document=document).entities

                        for entity in entities:
                            entity_type = language.Entity.Type(entity.type_)
                            print('=' * 20)
                            print(u'{:<16}~ {}'.format('url', url))
                            print(u'{:<16}: {}'.format('name', entity.name))
                            print(u'{:<16}: {}'.format('type', entity_type.name))
                            print(u'{:<16}: {}'.format('salience', entity.salience))
                            print(u'{:<16}: {}'.format('wikipedia_url', entity.metadata.get('wikipedia_url', '-')))
                            print(u'{:<16}: {}'.format('mid', entity.metadata.get('mid', '-')))

                            row = [url, entity.name, entity_type.name, entity.salience,
                                   entity.metadata.get("wikipedia_url"), entity.metadata.get("mid")]
                            filewriter.writerow(row)


        # This if statement handles if while loop continues or breaks based on user input
        decision = input('Run another analysis? (Y/N) ')
        if decision == 'N' or decision == 'n':
            break
