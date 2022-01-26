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
        #some os stuff
        if not os.path.exists(os.path.join(os.getcwd(), 'files')):
            os.mkdir('files')

    def scrape(self):
        base_url = 'https://www.lexico.com/definition/{}'
        with open("words.txt", "r") as file:
            words = file.read().split("\n")
        for word in words:
            try:
                page = requests.get(base_url.format(word), timeout=0.5).content
            except ConnectionError as e:
                print(e)
                
                return("No response")
            soup = BeautifulSoup(page, "html.parser")
            sections = soup.find_all("section", class_='gramb')
            full_definition = ''
            examples = ''
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
                #creating note 
            self.create_note(word, full_definition, examples)

    def create_note(self, word, definition, example, output_file_name='output.apkg', guid=None):
        my_note = genanki.Note(
            model=self.my_model,
            fields=[word, definition, example],
            guid=guid)
        self.my_deck.add_note(my_note)
        genanki.Package(self.my_deck).write_to_file('files/' + output_file_name)


#my own templates for GRE Vocabulary
my_qfmt = '<div class="front-side">{{Full definition}}</div><input type="text">'
my_afmt = """
<div class="word">{{Word}}</div>
<hr id="answer"><div class="definition-example">Full definition</div><br>
<div class="defition-example-actual">{{Full definition}}</div>
<div class='definition-example'>Examples</div><br>
<div class="defition-example-actual">{{Examples}}</div>"""

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
anki = AnkiVocabulary(my_qfmt, my_afmt, my_css, 18, 'GRE Vocabulary', 19, word_type_dic)
anki.scrape()