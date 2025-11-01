from fuzzywuzzy import fuzz

from card_database_loader import load_card_name_to_id_map, card_name_to_key, load_card

fuzzy_match_score_threshold_start = 90
fuzzy_match_score_threshold_step = 10
fuzzy_match_round = 2

card_name_to_id_map = None

def search_card_id(card_name):
    global card_name_to_id_map
    if card_name_to_id_map is None:
        card_name_to_id_map = load_card_name_to_id_map()
    card_name_keys = card_name_to_id_map.keys()

    card_name_key = card_name_to_key(card_name)

    found = []
    for round in range(fuzzy_match_round):
        for key in card_name_keys:
            fuzzy_match_score = fuzz.partial_ratio(card_name_key, key)
            if fuzzy_match_score >= fuzzy_match_score_threshold_start - round * fuzzy_match_score_threshold_step:
                found.append(card_name_to_id_map[key])
        if len(found) > 0:
            break

    return found

def search_card_name(card_name):
    card_ids = search_card_id(card_name)

    output = []
    for card_id in card_ids:
        card_info = load_card(card_id)
        card_name_actual = card_info["name"]
        output.append(card_name_actual)

    return output

