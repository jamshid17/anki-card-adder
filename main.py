from email.mime import audio
import genanki
import requests
from bs4 import BeautifulSoup
import os 



class AnkiVocabulary:
    def __init__(self, my_qfmt, my_afmt, my_css, model_id, deck_name, deck_id, word_type_dic):
        self.my_qfmt = my_qfmt
        self.my_afmy = my_afmt
        self.my_css = my_css
        self.model_id = model_id
        self.word_type_dic = word_type_dic

        #model
        self.my_model = genanki.Model(
        self.model_id,
        'My Model',
        fields=[
            {'name': 'Word'},
            {'name': 'Full definition'},
            {'name': 'Examples'},
            {'name': 'Music'},
        ],
        templates=[
            {
            'name': 'Card 1',
            'qfmt': my_qfmt,
            'afmt': my_afmt,
            },
        ],
        css=self.my_css,
        )
        self.my_deck = genanki.Deck(
            deck_id,
            deck_name)
        self.package = genanki.Package(self.my_deck)
        self.package.media_files = []
        #some os stuff
        if not os.path.exists(os.path.join(os.getcwd(), 'files')):
            os.mkdir('files')
        if not os.path.exists(os.path.join(os.getcwd(), 'files', 'media')):
            os.chdir('files')
            os.mkdir('media')
            os.chdir('../')

    def scrape(self):
        base_url = 'https://www.lexico.com/definition/{}'
        with open("words.txt", "r") as file:
            words = file.read().split("\n")
        for word in words:
            word = word.replace(' ', '')
            try:
                page = requests.get(base_url.format(word), timeout=0.5)
            except ConnectionError as e:
                print(e)
                
                return("No response")
            #finding out if word exists
            if page.status_code == 406:
                #creating not-found-words-txt file and inserting this word to this file
                with open('files/not-found.txt', 'a') as not_found_file:
                    not_found_file.write(word + '\n')
            else:
                soup = BeautifulSoup(page.content, "html.parser")
                sections = soup.find_all("section", class_='gramb')
                full_definition = ''
                examples = ''
                audio_name = None
                for section in sections:
                    word_type = section.find("span", class_='pos').text
                    if word_type in self.word_type_dic.keys():
                        word_type = self.word_type_dic[word_type]
                    try:
                        word_div = section.find('ul', class_='semb').find('div', class_='trg')
                        defi = word_div.find('p').find('span', class_='ind one-click-content').text.lower()
                        if word_type == 'verb':
                            defi = 'to ' + defi
                        full_definition += word_type + ':  ' + defi[:-1] + ";\n"
                    except:
                        pass
                    #example
                    try:
                        example = word_div.find('div', class_='examples').find('li').text
                        examples = '{}{};\n'.format(examples, example)
                    except:
                        pass
                #finding audio url and downloading
                try: 
                    audio_url = soup.find('a', class_='speaker').find('audio')['src']
                    audio_name = audio_url.split('/')[-1]
                    #downloading
                    audio_content = requests.get(audio_url).content
                    open('files/media/{}'.format(audio_name), 'wb').write(audio_content)
                except:
                    pass
                #creating note 
                if "_" in word:
                    word = word.replace("_", " ")
                self.create_note(word, full_definition, examples, audio_name)

    def create_note(self, word, definition, example, audio_name, output_file_name='output.apkg', guid=None):
        my_note = genanki.Note(
            model=self.my_model,
            fields=[word, definition, example,'[sound:{}]'.format(audio_name)],
            guid=guid)
        self.my_deck.add_note(my_note)
        self.package.media_files.append('files/media/{}'.format(audio_name))
        self.package.write_to_file('files/' + output_file_name)


#my own templates for GRE Vocabulary
my_qfmt = '<div class="front-side">{{Full definition}}</div><input type="text">'
my_afmt = """
<div class="word">{{Word}}</div>
<hr id="answer"><div class="definition-example">Full definition</div><br>
<div class="defition-example-actual">{{Full definition}}</div>
<div class='definition-example'>Examples</div><br>
<div class="defition-example-actual">{{Examples}}</div>
<div>{{ Music }}</div>
"""

my_css = """
.front-side{
    font-size: 20px;
}
input{
    width: 100%;
    height: 25px;
    font-size: 18px;
}
.word{
    font-size: 30px;
}
#answer{
    margin-bottom: 30px;
}
.definition-example{
    font-size: 18px;
    color:rgb(63, 152, 235);
    margin-bottom: -20px;
    padding: 0px;
}
.defition-example-actual{
    font-size: 20px;
    margin-bottom: 20px;
}
"""

word_type_dic = {
    "noun":"n", 
    "determiner":"det",
    "pronoun":'p-noun',
    "verb":"v", 
    "adjective":"adj", 
    "adverb":"adv", 
    "preposition":'preposition', 
    "conjunction":"conjunction"
}

#making class obj
anki = AnkiVocabulary(my_qfmt, my_afmt, my_css, 18, 'media test', 22, word_type_dic)
anki.scrape()