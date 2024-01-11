import random
from typing import List


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
def pick_top_k(global_models, k: int, assign_score=assign_score_mean):
    return list(
        map(
            lambda x: x[0],
            sorted(
                map(lambda x: (x[0], assign_score(x[1])), global_models),
                key=lambda x: x[1],
                reverse=True,
            )[:k],
        )
    )


def pick_top_3(global_models):
    return pick_top_k(global_models, 3)


def pick_top_2(global_models):
    return pick_top_k(global_models, 2)


def pick_random_k(global_models, k: int):
    return random.choices(list(map(lambda x: x[0], global_models)), k=k)


def pick_random_3(global_models):
    return pick_random_k(global_models, 3)


def pick_random_2(global_models):
    return pick_random_k(global_models, 2)


def pick_weighted_random_k(global_models, k: int, assign_score=assign_score_mean):
    return random.choices(
        list(map(lambda x: x[0], global_models)),
        weights=list(map(lambda x: assign_score(x[1]))),
        k=k,
    )


def pick_weighted_random_3(global_models):
    return pick_weighted_random_k(global_models, 3)


def pick_weighted_random_2(global_models):
    return pick_weighted_random_k(global_models, 2)


def pick_all(global_models):
    return list(map(lambda x: x[0], global_models))


def pick_above_mean(global_models, assign_score=assign_score_mean):
    mean_score = sum(list(map(lambda x: assign_score(x[1]), global_models))) / len(
        global_models
    )

    return list(
        map(
            lambda x: x[0],
            filter(lambda x: assign_score(x[1]) > mean_score, global_models),
        )
    )


def pick_above_median(global_models, assign_score=assign_score_mean):
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


def pick_above_self(global_models, self, assign_score=assign_score_mean):
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
