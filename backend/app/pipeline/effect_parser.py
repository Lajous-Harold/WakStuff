"""
Parser d'effets Wakfu basé sur l'article:
https://dev.to/heymarkkop/decoding-wakfu-s-action-effects-with-javascript-1nm2

Traduit de JavaScript vers Python pour décoder les descriptions d'actions
avec leurs paramètres complexes.
"""

import re
from typing import Any, Dict, List, Optional


# Mapping des éléments
ELEMENT_MAP = {
    1: {"fr": "Feu", "en": "Fire", "es": "Fuego", "pt": "Fogo"},
    2: {"fr": "Eau", "en": "Water", "es": "Agua", "pt": "Água"},
    3: {"fr": "Terre", "en": "Earth", "es": "Tierra", "pt": "Terra"},
    4: {"fr": "Air", "en": "Air", "es": "Aire", "pt": "Ar"},
    5: {"fr": "Lumière", "en": "Light", "es": "Luz", "pt": "Luz"},
    6: {"fr": "Ténèbres", "en": "Shadow", "es": "Sombra", "pt": "Sombra"},
}


def parse_effect(
    effect: Dict[str, Any],
    level: int,
    actions_data: List[Dict[str, Any]],
    states_data: Optional[List[Dict[str, Any]]] = None,
    jobs_data: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Parse un effet pour enrichir sa description dans toutes les langues.

    Args:
        effect: Effet brut de l'API Wakfu
        level: Niveau de l'item
        actions_data: Liste des actions (actions.json)
        states_data: Liste des états (states.json) - optionnel
        jobs_data: Liste des jobs (jobs.json) - optionnel

    Returns:
        Effet enrichi avec description parsée
    """
    if not effect or not isinstance(effect, dict):
        return effect

    definition = effect.get("definition", {})
    action_id = definition.get("actionId")

    if not action_id:
        return effect

    # Cas spécial pour Makabrakfire (hardcodé)
    if action_id == 1020:
        effect["description"] = {
            "fr": "Renvoie 10% des dégâts",
            "en": "Reflects 10% of damage",
            "es": "Devuelve un 10% de los daños",
            "pt": "Reenvia 10% dos danos",
        }
        return effect

    # Trouver l'action correspondante
    action = next(
        (a for a in actions_data if a.get("definition", {}).get("id") == action_id),
        None,
    )

    if not action or "description" not in action:
        return effect

    original_params = definition.get("params", [])
    description_templates = action["description"]

    if not description_templates or not isinstance(description_templates, dict):
        return effect

    # Parser les paramètres (par paires: valeur_base + valeur_par_niveau)
    parsed_params = []
    for index in range(0, len(original_params), 2):
        if index + 1 > len(original_params):
            break

        param_number = (index // 2) + 1
        param_key = f"[#{param_number}]"

        base_value = original_params[index]
        level_value = original_params[index + 1] if index + 1 < len(original_params) else 0
        param_value = int(base_value + level_value * level)

        # Cas spéciaux selon l'actionId
        if action_id == 304 and index == 0:
            # Référence à un état
            state_id = original_params[0]
            if states_data:
                state = next(
                    (s for s in states_data if s.get("definition", {}).get("id") == state_id),
                    None,
                )
                if state and state.get("title"):
                    param_value = state["title"]
                else:
                    param_value = {"fr": "Effet inconnu", "en": "Unknown effect"}

        elif action_id == 832 and index == 0:
            # Référence à un élément
            element_id = original_params[0]
            param_value = ELEMENT_MAP.get(element_id, {"fr": "?", "en": "?"})

        elif action_id == 2001 and index == 2:
            # Référence à un job
            job_id = original_params[2]
            if jobs_data:
                job = next(
                    (j for j in jobs_data if j.get("definition", {}).get("id") == job_id),
                    None,
                )
                if job and job.get("title"):
                    param_value = job["title"]

        elif action_id == 39 and index == 4:
            # Référence à une caractéristique
            char_id = original_params[4]
            characteristic_map = {
                120: {
                    "fr": "Armure reçue",
                    "en": "Armor received",
                    "es": "Armadura recibida",
                    "pt": "de Armadura recebida",
                },
                121: {
                    "fr": "Armure donnée",
                    "en": "Armor given",
                    "es": "Armadura dada",
                    "pt": "de Armadura concedida",
                },
            }
            param_value = characteristic_map.get(char_id, {"fr": "?", "en": "?"})

        parsed_params.append(
            {"regex": re.escape(param_key), "value": param_value, "rawValue": param_value}
        )

    # Construire les descriptions pour chaque langue
    new_description = {}

    for lang, template in description_templates.items():
        try:
            parsed_desc = _parse_template(template, parsed_params, lang)
            new_description[lang] = parsed_desc
        except Exception as e:
            # En cas d'erreur, garder le template original
            new_description[lang] = template

    effect["description"] = new_description
    return effect


def _parse_template(template: str, parsed_params: List[Dict], lang: str) -> str:
    """
    Parse un template de description avec ses conditions et paramètres.

    Cette fonction reproduit la logique JavaScript de l'article:
    - Remplace les conditions {[>2]?s:} par leur résultat
    - Remplace les paramètres [#1] par leurs valeurs
    - Gère les opérateurs ~, +, -, <, >, =
    """
    result = template
    stack = 0  # Pile pour stocker la dernière valeur évaluée

    # Étape 1: Remplacer les paramètres [#N] et mettre à jour la stack
    for param in parsed_params:
        param_regex = param["regex"]
        param_value = param["value"]

        # Si c'est un dict multilingue, prendre la bonne langue
        if isinstance(param_value, dict):
            param_value = param_value.get(lang, param_value.get("en", "?"))

        # Remplacer dans le template
        result = re.sub(param_regex, str(param_value), result)
        stack = param_value if isinstance(param_value, (int, float)) else 0

    # Étape 2: Évaluer les conditions
    # Format: {[condition]?valueIfTrue:valueIfFalse}

    # Traiter les conditions composées
    def eval_condition(match):
        nonlocal stack
        full_match = match.group(0)
        condition = match.group(1)
        true_val = match.group(2)
        false_val = match.group(3) if match.group(3) else ""

        # Parser la condition
        cond_result = _evaluate_condition(condition, parsed_params, stack)

        # Mettre à jour stack si nécessaire
        if cond_result and isinstance(true_val, (int, float)):
            stack = true_val

        return true_val if cond_result else false_val

    # Pattern pour détecter {[condition]?true:false}
    condition_pattern = r"\{([^\}]+)\?([^:]*):([^\}]*)\}"

    # Remplacer itérativement jusqu'à ce qu'il n'y ait plus de conditions
    max_iterations = 20
    for _ in range(max_iterations):
        if not re.search(condition_pattern, result):
            break
        result = re.sub(condition_pattern, eval_condition, result)

    # Nettoyer les tags spéciaux restants
    result = _clean_special_tags(result, lang)

    return result


def _evaluate_condition(condition: str, parsed_params: List[Dict], stack: int) -> bool:
    """
    Évalue une condition comme [~3], [+2], [>5], etc.

    Opérateurs:
    - [~N]: len(params) >= N
    - [+N]: len(params) > N
    - [-N]: len(params) < N
    - [>N]: stack >= N
    - [<N]: stack <= N
    - [=N]: stack == N
    - [N=M]: params[M-1] == N
    - [N<M]: params[M-1] < N
    - [N>M]: params[M-1] > N
    """
    condition = condition.strip("[]")

    # Opérateurs sur la longueur des paramètres
    if condition.startswith("~"):
        n = int(condition[1:])
        return len(parsed_params) >= n
    if condition.startswith("+"):
        n = int(condition[1:])
        return len(parsed_params) > n
    if condition.startswith("-"):
        n = int(condition[1:])
        return len(parsed_params) < n

    # Opérateurs sur la stack
    if condition.startswith(">"):
        n = int(condition[1:])
        return stack >= n
    if condition.startswith("<"):
        n = int(condition[1:])
        return stack <= n
    if condition.startswith("="):
        n = int(condition[1:])
        return stack == n

    # Opérateurs sur les paramètres indexés
    # Format: [N op M] où N est une valeur, op est =/</>. M est l'index du paramètre
    match = re.match(r"(\d+)([=<>])(\d+)", condition)
    if match:
        value = int(match.group(1))
        operator = match.group(2)
        param_index = int(match.group(3)) - 1

        if 0 <= param_index < len(parsed_params):
            param_raw = parsed_params[param_index]["rawValue"]
            if isinstance(param_raw, (int, float)):
                if operator == "=":
                    return param_raw == value
                elif operator == "<":
                    return param_raw < value
                elif operator == ">":
                    return param_raw > value

    return False


def _clean_special_tags(text: str, lang: str) -> str:
    """
    Nettoie les tags spéciaux comme [el6], [ecnbi], etc.

    Tags connus:
    - [elN]: Élément (N = 1-6)
    - [ecnbi], [ecnbr]: Icônes (on les supprime pour l'instant)
    """
    # Tags d'éléments
    for elem_id, elem_names in ELEMENT_MAP.items():
        text = text.replace(f"[el{elem_id}]", elem_names.get(lang, ""))

    # Supprimer les tags d'icônes inconnus
    text = re.sub(r"\[ecnb[ir]\]", "", text)
    text = re.sub(r"\[\w+\]", "", text)  # Supprimer tout tag restant

    return text.strip()


def parse_all_item_effects(
    item: Dict[str, Any],
    actions_data: List[Dict[str, Any]],
    states_data: Optional[List[Dict[str, Any]]] = None,
    jobs_data: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Parse tous les effets d'un item (equipEffects + useEffects).

    Args:
        item: Item brut de l'API
        actions_data: Liste des actions
        states_data: Liste des états
        jobs_data: Liste des jobs

    Returns:
        Item avec effets parsés dans le champ 'parsed_effects'
    """
    definition = item.get("definition", {})
    item_def = definition.get("item", {})
    level = item_def.get("level", 1)

    parsed_effects = {"equipEffects": [], "useEffects": []}

    # Parser equipEffects
    equip_effects = definition.get("equipEffects", [])
    for effect_wrapper in equip_effects:
        effect = effect_wrapper.get("effect", {})
        parsed = parse_effect(effect, level, actions_data, states_data, jobs_data)
        parsed_effects["equipEffects"].append(parsed)

    # Parser useEffects
    use_effects = definition.get("useEffects", [])
    for effect_wrapper in use_effects:
        effect = effect_wrapper.get("effect", {})
        parsed = parse_effect(effect, level, actions_data, states_data, jobs_data)
        parsed_effects["useEffects"].append(parsed)

    return parsed_effects
