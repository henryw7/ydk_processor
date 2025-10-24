
def counter_map(item_list):
    result = {}
    for item in item_list:
        result[item] = result.get(item, 0) + 1
    return result

class Deck:
    def __init__(self):
        self.main = []
        self.extra = []
        # self.side = []

    def __str__(self):
        return f"main deck: {self.main}, extra deck: {self.extra}"

    def sanity_check(self):
        assert type(self.main)  is list
        assert type(self.extra) is list
        assert len(self.main) >= 40 or len(self.main) <= 60, \
            f"Incorrect main deck size = {len(self.main)}"
        assert len(self.extra) <= 15, \
            f"Incorrect extra deck size = {len(self.extra)}"

        main_and_extra = self.main + self.extra
        assert not any([not type(id) is int or id > 99999999 or id < 0 for id in main_and_extra]), \
            "Incorrect card id in the deck"

        main_card_count = counter_map(main_and_extra)
        if any([n[1] > 3 for n in main_card_count.items()]):
            for key, value in main_card_count.items():
                if value > 3:
                    print(f"There are {value} of card {key} in the deck")
            assert False, "More than 3 of the same cards in the deck"

def read_ydk(filename):
    file_handle = open(filename, "r")
    file_lines = file_handle.readlines()
    file_handle.close()

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
    # deck.side = result["side"]
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
    # file_lines.extend([str(id) + "\n" for id in deck.side])
    file_lines.append("\n")

    file_handle = open(filename, "w")
    file_handle.writelines(file_lines)
    file_handle.close()
    print(f"Writing to {filename} done.")
