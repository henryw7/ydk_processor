from card_database_loader import load_card, card_type_values

def counter_map(item_list):
    result = {}
    for item in item_list:
        result[item] = result.get(item, 0) + 1
    return result

class Deck:
    def __init__(self):
        self.main = []
        self.extra = []
        self.side_main = []
        self.side_extra = []

    def __str__(self):
        output = "main deck:\n"
        for card_id in self.main:
            card_info = load_card(card_id)
            output += f"{card_id} : {card_info["name"]}\n"
        output += "\nextra deck:\n"
        for card_id in self.extra:
            card_info = load_card(card_id)
            output += f"{card_id} : {card_info["name"]}\n"
        output += "\nside:\n"
        for card_id in self.side_main + self.side_extra:
            card_info = load_card(card_id)
            output += f"{card_id} : {card_info["name"]}\n"
        return output

    def sanity_check(self):
        assert type(self.main)  is list
        assert type(self.extra) is list
        assert len(self.main) >= 40 or len(self.main) <= 60, \
            f"Incorrect main deck size = {len(self.main)}"
        assert len(self.extra) <= 15, \
            f"Incorrect extra deck size = {len(self.extra)}"
        assert len(self.side_main) + len(self.side_extra) <= 15, \
            f"Incorrect side size = {len(self.side_main) + len(self.side_extra)}"

        for card_id in self.main:
            card_info = load_card(card_id)
            card_type = card_info["type"]
            card_location = card_type_values[card_type]
            assert card_location == "main", \
                f"Card {card_id} ({card_info["name"]}) does not belong to main deck"
        for card_id in self.extra:
            card_info = load_card(card_id)
            card_type = card_info["type"]
            card_location = card_type_values[card_type]
            assert card_location == "extra", \
                f"Card {card_id} ({card_info["name"]}) does not belong to extra deck"

        all_cards = self.main + self.extra + self.side_main + self.side_extra
        assert not any([not type(id) is int or id > 99999999 or id < 0 for id in all_cards]), \
            "Incorrect card id in the deck"

        main_card_count = counter_map(all_cards)
        if any([n[1] > 3 for n in main_card_count.items()]):
            for key, value in main_card_count.items():
                if value > 3:
                    print(f"There are {value} of card {key} in the deck")
            assert False, "More than 3 of the same cards in the deck"

def read_ydk(filename):
    with open(filename, "r") as file_handle:
        file_lines = file_handle.readlines()

    result = { "main" : [], "extra" : [], "side" : [] }
    now_updating = None
    for line in file_lines:
        if line.startswith("#main"):
            assert now_updating != "main"
            now_updating = "main"
        elif line.startswith("#extra"):
            assert now_updating != "extra"
            now_updating = "extra"
        elif line.startswith("!side"):
            assert now_updating != "side"
            now_updating = "side"
        else:
            assert now_updating is not None
            fields = line.split()
            if len(fields) == 0:
                pass
            else:
                card_id = int(fields[0])
                result[now_updating].append(card_id)

    deck = Deck()
    deck.main = result["main"]
    deck.extra = result["extra"]

    deck.side_main = []
    deck.side_extra = []
    for card_id in result["side"]:
        card_info = load_card(card_id)
        card_type = card_info["type"]
        card_location = card_type_values[card_type]
        if card_location == "main":
            deck.side_main.append(card_id)
        elif card_location == "extra":
            deck.side_extra.append(card_id)
        else:
            raise ValueError(f"Unrecognized card_type {card_type} at location {card_location}")
    return deck

def write_ydk(filename, deck):
    assert type(deck) is Deck

    file_lines = []
    file_lines.append("#main \n")
    file_lines.extend([str(id) + "\n" for id in deck.main])
    file_lines.append("\n")
    file_lines.append("#extra \n")
    file_lines.extend([str(id) + "\n" for id in deck.extra])
    file_lines.append("\n")
    file_lines.append("!side \n")
    file_lines.extend([str(id) + "\n" for id in (deck.side_main + deck.side_extra)])
    file_lines.append("\n")

    with open(filename, "w") as file_handle:
        file_handle.writelines(file_lines)
    print(f"Writing to {filename} done.")
