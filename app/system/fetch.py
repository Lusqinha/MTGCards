from mtgsdk import Card
from json import dumps, loads
from sys import argv

class MTGCards:
    languages = [
        "Portuguese (Brazil)",
        "English",
        "Chinese Simplified",
        "Chinese Traditional",
        "French",
        "German",
        "Italian",
        "Japanese",
        "Korean",
        "Russian",
        "Spanish",
    ]
    def __init__(self):
        self.cards = []
    
    def remove_non_ptbr(self, card_entry:dict, language:str=languages[0]):
        target_language = language
        target_foreign_language = None
            
        if 'foreign_names' in card_entry and card_entry['foreign_names'] != None:
            for foreign_name in card_entry['foreign_names']:
                if foreign_name['language'] == target_language:
                    target_foreign_language = foreign_name
                    break
                
            if target_foreign_language:
                relevant_translations = [
                    foreign_name for foreign_name in card_entry["foreign_names"] if foreign_name["language"] == target_language
                ]
                
                card_output = {
                    key: value for key, value in card_entry.items() if key != "foreign_names"
                }
                card_output["foreign_names"] = relevant_translations

                card_output_json = dumps(card_output, indent=4)
                
                card_output = card_output_json
                return loads(card_output)
            else:
                print("No card found")
                return card_entry
        else:
            print("No foreign names found in card entry")
            return card_entry
        
    def find_one_by_name(self, card_name:str):
        card_output = {}
        
        try:
            cards:list = Card.where(name=card_name).all()
            card_entry = cards[0].__dict__

            card_output = self.remove_non_ptbr(card_entry)
        except IndexError:
            print("Card not found in English")

            cards:list = Card.where(language=self.languages[0]).where(name=card_name).all()
            card_entry = cards[0].__dict__
            
            card_output = self.remove_non_ptbr(card_entry)
        finally:
            return card_output
        
    def fetch_many_by_name(self, card_name:str):
        card_output = []
        try:
            cards:list = Card.where(name=card_name).all()
            for card in cards:
                card_entry = card.__dict__
                card_output.append(card_entry)
            if len(card_output) == 0:
                raise IndexError
        except (IndexError):
            print("Card not found in English: ", card_name)

            cards:list = Card.where(language=self.languages[0]).where(name=card_name).all()
            for card in cards:
                card_entry = card.__dict__
                card_output.append(card_entry)
        finally:
            return card_output
        
    def fetch_by_id(self, card_id, card_name):
        card = Card.where(name=card_name).where(id=card_id).all()[0]
        card_entry = card.__dict__
        card_output = self.remove_non_ptbr(card_entry)
        return card_output
    
    def fetch_by_img(self, img_url):
        card = Card.where(image_url=img_url).all()[0]
        card_entry = card.__dict__
        card_output = self.remove_non_ptbr(card_entry)
        return card_output

    def fetch_by_multiverse_id(self, multiverse_id):
        card = Card.where(multiverse_id=multiverse_id).all()[0]
        card_entry = card.__dict__
        card_output = self.remove_non_ptbr(card_entry)
        return card_output
        
        
        
if __name__ == '__main__':
    mtg_cards = MTGCards()
    print(mtg_cards.fetch_by_multiverse_id(argv[1]))
        