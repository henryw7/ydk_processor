import urllib.request
import json
import yaml
import re
from dateutil.parser import parse as parse_date

url_ygoprodeck_version = "https://db.ygoprodeck.com/api/v7/checkDBVer.php"
url_ygoprodeck_all_cards = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
url_ygoprodeck_all_sets = "https://db.ygoprodeck.com/api/v7/cardsets.php"

cachefile_version = "data/version.yaml"
cachefile_all_sets = "data/all_sets.yaml"
cachefile_card_name_map = "data/card_name_to_id_map.yaml"
cachefile_cards_template = "data/cards/%s.yaml"

n_all_cards_split = 100

special_character_to_english = {
    'α': 'alpha',
    'β': 'beta',
    'γ': 'gamma',
    'δ': 'delta',
    'ε': 'epsilon',
    'ζ': 'zeta',
    'η': 'eta',
    'θ': 'theta',
    'ι': 'iota',
    'κ': 'kappa',
    'λ': 'lambda',
    'μ': 'mu',
    'ν': 'nu',
    'ξ': 'xi',
    'ο': 'omicron',
    'π': 'pi',
    'ρ': 'rho',
    'σ': 'sigma',
    'τ': 'tau',
    'υ': 'upsilon',
    'φ': 'phi',
    'χ': 'chi',
    'ψ': 'psi',
    'ω': 'omega',
    'Α': 'Alpha',
    'Β': 'Beta',
    'Γ': 'Gamma',
    'Δ': 'Delta',
    'Ε': 'Epsilon',
    'Ζ': 'Zeta',
    'Η': 'Eta',
    'Θ': 'Theta',
    'Ι': 'Iota',
    'Κ': 'Kappa',
    'Λ': 'Lambda',
    'Μ': 'Mu',
    'Ν': 'Nu',
    'Ξ': 'Xi',
    'Ο': 'Omicron',
    'Π': 'Pi',
    'Ρ': 'Rho',
    'Σ': 'Sigma',
    'Τ': 'Tau',
    'Υ': 'Upsilon',
    'Φ': 'Phi',
    'Χ': 'Chi',
    'Ψ': 'Psi',
    'Ω': 'Omega',
    '+': 'plus',
    '＋': 'plus',
    # '-': 'minus', # This is also dash
    '−': 'minus',
}

def replace_special_characters(text):
    converted = []
    for char in text:
        if char in special_character_to_english:
            converted.append(' ' + special_character_to_english[char])
        else:
            converted.append(char)
    return ''.join(converted)

def card_name_to_key(card_name):
    card_name_key = card_name
    card_name_key = replace_special_characters(card_name_key)
    card_name_key = re.sub(r'[^a-zA-Z0-9]', ' ', card_name_key)
    card_name_key = re.sub(r'\s+', ' ', card_name_key.strip())
    card_name_key = card_name_key.lower()
    return card_name_key

card_type_values = {
    "Effect Monster" : "main",
    "Flip Effect Monster" : "main",
    "Flip Tuner Effect Monster" : "main",
    "Gemini Monster" : "main",
    "Normal Monster" : "main",
    "Normal Tuner Monster" : "main",
    "Pendulum Effect Monster" : "main",
    "Pendulum Effect Ritual Monster" : "main",
    "Pendulum Flip Effect Monster" : "main",
    "Pendulum Normal Monster" : "main",
    "Pendulum Tuner Effect Monster" : "main",
    "Ritual Effect Monster" : "main",
    "Ritual Monster" : "main",
    "Spell Card" : "main",
    "Spirit Monster" : "main",
    "Toon Monster" : "main",
    "Trap Card" : "main",
    "Tuner Monster" : "main",
    "Union Effect Monster" : "main",

    "Fusion Monster" : "extra",
    "Link Monster" : "extra",
    "Pendulum Effect Fusion Monster" : "extra",
    "Synchro Monster" : "extra",
    "Synchro Pendulum Effect Monster" : "extra",
    "Synchro Tuner Monster" : "extra",
    "XYZ Monster" : "extra",
    "XYZ Pendulum Effect Monster" : "extra",

    "Skill Card" : "other",
    "Token" : "other",
}

card_frameType_values = [
    "normal",
    "effect",
    "ritual",
    "fusion",
    "synchro",
    "xyz",
    "link",
    "normal_pendulum",
    "effect_pendulum",
    "ritual_pendulum",
    "fusion_pendulum",
    "synchro_pendulum",
    "xyz_pendulum",
    "spell",
    "trap",
    "token",
    "skill",
]

def print_json(json_obj):
    print(json.dumps(json_obj, indent = 4))

def fetch_url(url):
    request_url = urllib.request.urlopen(url)
    response_str = request_url.read()
    response_json = json.loads(response_str)
    return response_json

def load_all_sets():
    with open(cachefile_all_sets, "r") as file_handle:
        cached_sets = yaml.safe_load(file_handle)
    return cached_sets

loaded_card_cache = {}

def load_all_cards():
    global loaded_card_cache
    cached_cards = {}
    for i_bundle in range(n_all_cards_split):
        cachefile_cards = cachefile_cards_template %(f"{i_bundle:03d}")
        with open(cachefile_cards, "r") as file_handle:
            cached_cards_bundle = yaml.safe_load(file_handle)
            cached_cards.update(cached_cards_bundle)
    loaded_card_cache = cached_cards
    return cached_cards

def load_card(card_id):
    global loaded_card_cache
    if card_id in loaded_card_cache:
        return loaded_card_cache[card_id]
    i_bundle = int(card_id) % n_all_cards_split
    cachefile_cards = cachefile_cards_template %(f"{i_bundle:03d}")
    with open(cachefile_cards, "r") as file_handle:
        cached_cards = yaml.safe_load(file_handle)
    loaded_card_cache.update(cached_cards)
    return cached_cards[card_id]

def load_card_name_to_id_map():
    with open(cachefile_card_name_map, "r") as file_handle:
        cached_card_name_map = yaml.safe_load(file_handle)
    return cached_card_name_map

if __name__ == '__main__':
    version_json = fetch_url(url_ygoprodeck_version)
    version_json = version_json[0]
    assert "database_version" in version_json
    assert "last_update" in version_json

    with open(cachefile_version, "r") as file_handle:
        cached_version = yaml.safe_load(file_handle)
    if cached_version is None:
        cached_version = {}

    if version_json["database_version"] == cached_version.get("database_version", "0.0") \
        and version_json["last_update"] == cached_version.get("last_update", "2000-01-01 00:00:00"):
        print("YGOProDeck database already up to date")
        exit()

    sets_json = fetch_url(url_ygoprodeck_all_sets)
    assert len(sets_json) > 0
    print_json(sets_json)

    cached_sets = {}
    for pack in sets_json:
        set_name = pack["set_name"]
        set_code = pack["set_code"]
        set_num_of_cards = pack["num_of_cards"]
        if "tcg_date" in pack:
            set_tcg_date = pack["tcg_date"]
        else:
            print(f"Warning: Set \"{set_name}\" has no \"tcg_date\" keyword")
            set_tcg_date = "9999-12-31"

        assert set_name not in cached_sets, set_name
        cached_sets[set_name.lower()] = {
            "code" : set_code,
            "name" : set_name,
            "num_of_cards" : set_num_of_cards,
            "tcg_date" : set_tcg_date,
        }

    with open(cachefile_all_sets, "w") as file_handle:
        yaml.dump(cached_sets, file_handle)

    cards_json = fetch_url(url_ygoprodeck_all_cards)
    cards_json = cards_json["data"]
    assert len(cards_json) > 0
    # print_json(cards_json)

    cached_card_name_map = {}
    cached_cards_bundle = [{} for i in range(n_all_cards_split)]
    for card in cards_json:
        # print_json(card)

        card_id = int(card["id"])
        card_name = card["name"]
        card_type = card["type"]
        card_humanReadableCardType = card["humanReadableCardType"]
        card_frameType = card["frameType"]
        card_description = card["desc"]

        assert card_type in card_type_values, card_type
        assert card_frameType in card_frameType_values, card_frameType

        cached_card_sets = []
        card_earliest_release_date = "9999-12-31"
        if "card_sets" in card:
            card_sets = card["card_sets"]
            assert len(card_sets) > 0

            for card_set in card_sets:
                set_name = card_set["set_name"]
                set_code = card_set["set_code"]
                set_rarity = card_set["set_rarity"]
                assert set_name.lower() in cached_sets, set_name
                set_tcg_date = cached_sets[set_name.lower()]["tcg_date"]
                if parse_date(set_tcg_date) < parse_date(card_earliest_release_date):
                    card_earliest_release_date = set_tcg_date

                cached_card_sets.append({
                    "name" : set_name,
                    "code" : set_code,
                    "rarity" : set_rarity,
                    "tcg_date" : set_tcg_date,
                })
        else:
            print(f"Warning: Card \"{card_name}\" has no \"card_sets\" keyword")

        i_bundle = card_id % n_all_cards_split
        assert card_id not in cached_cards_bundle[i_bundle]
        cached_cards_bundle[i_bundle][card_id] = {
            "id" : card_id,
            "name" : card_name,
            "type" : card_type,
            "humanReadableCardType" : card_humanReadableCardType,
            "frameType" : card_frameType,
            "description" : card_description,
            "earliest_release_date" : card_earliest_release_date,
            "sets" : cached_card_sets,
        }

        card_name_key = card_name_to_key(card_name)
        assert card_name_key not in cached_card_name_map, (card_name, card_name_key)
        cached_card_name_map[card_name_key] = card_id

    for i_bundle in range(n_all_cards_split):
        cachefile_cards = cachefile_cards_template %(f"{i_bundle:03d}")
        with open(cachefile_cards, "w") as file_handle:
            yaml.dump(cached_cards_bundle[i_bundle], file_handle)

    with open(cachefile_card_name_map, "w") as file_handle:
        yaml.dump(cached_card_name_map, file_handle)

    cached_version["database_version"] = version_json["database_version"]
    cached_version["last_update"] = version_json["last_update"]
    with open(cachefile_version, "w") as file_handle:
        yaml.dump(cached_version, file_handle)
