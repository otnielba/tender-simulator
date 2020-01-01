import numpy as np
import pandas as pd
import random
import time

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
This solution is a simplified version of a common solution to the Multiple-Choice Knapsack Problem.
This solution can be optimized using dynamic programing.

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
start = time.time()


"""""""""""""""""""""
Tender Parameters
"""""""""""""""""""""

a_limit = 5
b_limit = 5
c_limit = 6
d_limit = 10
e_limit = 10
num_of_players = 9
empty_v = {'a' : 0, 'b' : 0 , 'c': 0, 'd' : 0, 'e' : 0, 'price' : 0}
iterations = 0

"""""""""""""""""""""""""""
      Random Setup
"""""""""""""""""""""""""""

def gen_master_matrix():
    vectors = []
    for i in range(0, a_limit + 1):
        for j in range(0, b_limit + 1):
            for k in range(0, c_limit + 1):
                for l in range(0, d_limit + 1):
                    for m in range(0, e_limit + 1):
                        vectors.append({'a' : i, 'b' : j , 'c': k, 'd' : l, 'e' : m, 'price_bid': 0})
    return vectors

def gen_players(n):
    players = []
    for player_id in range(1, n+1):
        player_vectors = all_vectors.sample(n= random.randint(30,50)) # sample a set of vectors from the 'all possibilities' vectors list
        player_vectors['price_bid'] = np.random.randint(1, 200, player_vectors.shape[0]) # set a random price_bid
        player_vectors.insert(0, 'player_id', player_id)  # add a player id column and reindex
        player_vectors.index = pd.RangeIndex(len(player_vectors.index))

        # add an empty vector so we can 'ignore' this player when scanning all combinations
        player_vectors.loc[-1] = [player_id, 0,0,0,0,0,0]
        player_vectors.index += 1  # shifting index
        player_vectors = player_vectors.sort_index()
        players.append(player_vectors)
    return players


"""""""""""""""""""""""""""
Vectors helper functions
"""""""""""""""""""""""""""

def is_tender_valid(cumulative_vector):
    return cumulative_vector['a'] <= a_limit and \
           cumulative_vector['b'] <= b_limit and \
           cumulative_vector['c'] <= c_limit and \
           cumulative_vector['d'] <= d_limit and \
           cumulative_vector['e'] <= e_limit

def sum_vectors(v1, v2):
    return {'a': v1['a'] + v2['a'],
            'b': v1['b'] + v2['b'],
            'c': v1['c'] + v2['c'],
            'd': v1['d'] + v2['d'],
            'e': v1['e'] + v2['e']}


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Recursively check all vector combinations, one of each tender player.
We keep track of the vectors cumulative sum of each parameter to check if we didn't break the tender rules.
and always check if we found the optimal combination from the tender's admin perspective (e.g. maximum price_bid)

@cur_players_vectors: a single vector denoting the currently examined combination of players vectors.

@cur_players_vectors_indexes: an index array of the players vectors that represents 'temp_players_vectors'
an example in a 3 players scenario, a temp_players_vectors_indexes = [1, 5, 0] means the combined vector
(e.g. @temp_players_vectors) is based on player #1 first vector in their list of vectors, players #2 fifth vector,
and non of player #3 vectors.

@temp_bid_sum: denotes the sum of players bids for the current vector combination

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def combine_next_player(player_index,
                        cur_players_vectors,
                        cur_players_vectors_indexes,
                        cur_bids_sum):

    if player_index >= len(tender_players):
        return

    player = tender_players[player_index]
    # iterate over the players vectors and check if this combination is valid and optimal
    for vector_index, vector in player.iterrows():
        global iterations
        iterations += 1

        # check if adding this player's vector to the current combination is still valid by the tender rules
        cur_players_vectors_indexes[player_index] = vector_index
        new_players_vectors  = sum_vectors(cur_players_vectors, vector)
        if not is_tender_valid(new_players_vectors):
            continue

        # check if the newly combined vector qualifies as the optimal/maximal bid
        new_combination = list(cur_players_vectors_indexes)
        result['valid_combs'].append(new_combination)
        if  result['max_price_bid'] < cur_bids_sum + vector['price_bid']:
            result['max_price_bid'] = cur_bids_sum
            result['optimal_combination'] = new_combination

        # next_player = player_index + 1
        combine_next_player(player_index= player_index + 1,
                            cur_players_vectors=new_players_vectors,
                            cur_players_vectors_indexes=new_combination,
                            cur_bids_sum=cur_bids_sum + vector['price_bid'])

# Generate all possible vectors
all_vectors = pd.DataFrame(gen_master_matrix())

# Generate 'players' with their tender offer (i.e. a list of vector)
tender_players = gen_players(num_of_players)
all_players_vectors = pd.concat(tender_players)

print("\n----------------------------------------------")
print("---------- Vectors of all players ------------")
print(all_players_vectors)
print("----------------------------------------------\n")

result = {'max_price_bid': 0,
          'optimal_combination': [],
          'valid_combs': []}

""" kickoff the recursive combination of all players vectors """
combine_next_player(player_index=0,
                    cur_players_vectors=empty_v,
                    cur_players_vectors_indexes=[0] * num_of_players,
                    cur_bids_sum=0)


all_vectors_combinations = np.prod([len(p) for p in tender_players])
all_valid_combinations = len(result['valid_combs'])

print("# of combinations: ", all_vectors_combinations)
print("# of iterations:", iterations)
print("# of valid combinations: ", all_valid_combinations)
print("ratio: {0:.5f} %".format(100 * all_valid_combinations / all_vectors_combinations))
print("sum of maximal valid bids:", result['max_price_bid'])
print("optimal combination (players indexes): ", result['optimal_combination'])


""""""""""""""""""""""""""""""""""""""""""
""" print the optimal players' vectors """
""""""""""""""""""""""""""""""""""""""""""
optimal_vectors = pd.DataFrame()
for pi, i in enumerate(result['optimal_combination']):
    player_vector = tender_players[pi].loc[[i]]
    optimal_vectors = pd.concat([optimal_vectors, player_vector]) if not optimal_vectors.empty else player_vector

optimal_vectors.index = pd.RangeIndex(len(optimal_vectors.index))
print("\n", optimal_vectors)
print("\n", "total runtime", time.time() - start)
