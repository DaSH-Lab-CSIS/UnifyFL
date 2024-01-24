import random
from typing import List, Optional


def pick_selected_model(
    global_models,
    aggregation_policy: str,
    scoring_policy: str,
    k: Optional[int] = None,
    mine: Optional[str] = None,
):
    assign_score_dict = {
        key.__name__: key
        for key in [
            assign_score_min,
            assign_score_max,
            assign_score_mean,
            assign_score_median,
            assign_score_random,
        ]
    }

    assign_score = assign_score_dict[scoring_policy]
    print("type",global_models)

    match aggregation_policy:
        case "pick_top_k":
            return pick_top_k(global_models, k, assign_score)
        case "pick_top_3":
            return pick_top_k(global_models, 3, assign_score)
        case "pick_top_2":
            return pick_top_k(global_models, 2, assign_score)
        case "pick_random_k":
            return pick_random_k(global_models, k)
        case "pick_random_3":
            return pick_random_k(global_models, 3)
        case "pick_random_2":
            return pick_random_k(global_models, 2)
        case "pick_weighted_random_k":
            return random.choices(
                list(map(lambda x: x[0], global_models)),
                weights=list(map(lambda x: assign_score(x[1]))),
                k=k,
            )
        case "pick_weighted_random_3":
            return pick_weighted_random_k(global_models, 3, assign_score)
        case "pick_weighted_random_2":
            return pick_weighted_random_k(global_models, 2, assign_score)
        case "pick_all":
            return list(map(lambda x: x[0], global_models))
        case "pick_above_mean":
            mean_score = sum(
                list(map(lambda x: assign_score(x[1]), global_models))
            ) / len(global_models)

            return list(
                map(
                    lambda x: x[0],
                    filter(lambda x: assign_score(x[1]) > mean_score, global_models),
                )
            )
        case "pick_above_median":
            scores = list(map(lambda x: assign_score(x[1]), global_models))

            return list(
                map(
                    lambda x: x[0],
                    filter(
                        lambda x: assign_score(x[1]) > sorted(scores)[len(scores) // 2],
                        global_models,
                    ),
                )
            )
        case "pick_self":
            return [mine]
        case "pick_above_self":
            self_score = assign_score(
                list(filter(lambda x: x[0] == mine, global_models))[1]
            )
            mmaa =  list(
                map(
                    lambda x: x[0],
                    filter(
                        lambda x: assign_score(x[1]) > self_score,
                        global_models,
                    ),
                )
            ) 
            if  len(mmaa) == 0:
                return [mine]
            else:
                return mmaa


# Score assignment helpers
def assign_score_min(scores: List[int]):
    return min(scores) if len(scores) > 0 else 0


def assign_score_max(scores: List[int]):
    return max(scores) if len(scores) > 0 else 0


def assign_score_mean(scores: List[int]):
    return sum(scores) / len(scores) if len(scores) > 0 else 0


def assign_score_median(scores: List[int]):
    return sorted(scores)[len(scores) // 2] if len(scores) > 0 else 0


def assign_score_random(scores: List[int]):
    return random.choice(scores) if len(scores) > 0 else 0


# Simple policies
def pick_top_k(global_models, k: int, assign_score):
    return list(
        map(
            lambda x: x[0],
            sorted(
                map(lambda x: (x[0], assign_score(x[1])), global_models),
                key=lambda x: x[1],
                reverse=True,
            )
        )
    )[:k]


def pick_top_3(global_models, assign_score):
    return pick_top_k(global_models, 3, assign_score)


def pick_top_2(global_models, assign_score):
    return pick_top_k(global_models, 2, assign_score)


def pick_random_k(global_models, k: int):
    if len(global_models) < k:
        return list(map(lambda x: x[0], global_models))
    return random.choices(list(map(lambda x: x[0], global_models)), k=k)


def pick_random_3(global_models):
    return pick_random_k(global_models, 3)


def pick_random_2(global_models):
    return pick_random_k(global_models, 2)


def pick_weighted_random_k(global_models, k: int, assign_score):
    return random.choices(
        list(map(lambda x: x[0], global_models)),
        weights=list(map(lambda x: assign_score(x[1]))),
        k=k,
    )


def pick_weighted_random_3(global_models, assign_score):
    return pick_weighted_random_k(global_models, 3, assign_score)


def pick_weighted_random_2(global_models, assign_score):
    return pick_weighted_random_k(global_models, 2, assign_score)


def pick_all(global_models):
    return list(map(lambda x: x[0], global_models))


def pick_above_mean(global_models, assign_score):
    mean_score = sum(list(map(lambda x: assign_score(x[1]), global_models))) / len(
        global_models
    )

    return list(
        map(
            lambda x: x[0],
            filter(lambda x: assign_score(x[1]) > mean_score, global_models),
        )
    )


def pick_above_median(global_models, assign_score):
    scores = list(map(lambda x: assign_score(x[1]), global_models))

    return list(
        map(
            lambda x: x[0],
            filter(
                lambda x: assign_score(x[1]) > sorted(scores)[len(scores) // 2],
                global_models,
            ),
        )
    )


def pick_self():
    return []


def pick_above_self(global_models, self, assign_score):
    self_score = assign_score(list(filter(lambda x: x[0] == self, global_models))[1])

    return list(
        map(
            lambda x: x[0],
            filter(
                lambda x: assign_score(x[1]) > self_score,
                global_models,
            ),
        )
    )


# Complex policies

# - [ ] Alternating between policies across rounds
# - [ ] Having a strict accuracy cutoff, after which it chooses to fine-tune its own model without merging external models.
