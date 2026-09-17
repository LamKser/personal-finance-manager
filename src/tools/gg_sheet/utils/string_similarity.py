# Source: https://www.geeksforgeeks.org/dsa/jaro-and-jaro-winkler-similarity/

def jaro_distance(string_1: str, string_2: str):
    if (string_1 == string_2):
        return 1.0 

    len_string_1 = len(string_1)
    len_string_2 = len(string_2) 
    
    if (len_string_1 == 0 or len_string_2 == 0):
        return 0.0

    max_dist = (max(len(string_1), len(string_2)) // 2 ) - 1 
    match = 0 
    hash_string_1 = [0] * len(string_1) 
    hash_string_2 = [0] * len(string_2)  

    for i in range(len_string_1):
        start = max(0, i - max_dist)
        end = min(len_string_2, i + max_dist + 1)
        for j in range(start, end): 
            if (string_1[i] == string_2[j] and hash_string_2[j] == 0): 
                hash_string_1[i] = 1 
                hash_string_2[j] = 1 
                match += 1 
                break 
        
    if (match == 0):
        return 0.0 

    t = 0
    point = 0 
    for i in range(len_string_1): 
        if (hash_string_1[i]):
            while (hash_string_2[point] == 0):
                point += 1 
            if (string_1[i] != string_2[point]):
                point += 1
                t += 1
            else:
                point += 1
                
        t /= 2 

    return ((match / len_string_1 + match / len_string_2 +
            (match - t) / match ) / 3.0) 


def jaro_winkler_similarity(string_1: str, string_2: str, max_len_prefix: int = 4, scale_factor: float = 0.1): 
    jaro_dist = jaro_distance(string_1, string_2) 
    prefix = 0 
    start = min(len(string_1), len(string_2))
    for i in range(start):
        if (string_1[i] == string_2[i]):
            prefix += 1
        else:
            break 

    prefix = min(max_len_prefix, prefix) 
    jaro_dist = jaro_dist + (scale_factor * prefix * (1 - jaro_dist) )
    return jaro_dist 
