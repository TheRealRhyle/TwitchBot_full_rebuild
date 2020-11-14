# Manifest is a List of Tuples that we will iterate through.
manifest = [("bananas" , 15), ("mattresses",34) , ("dog kennels", 42), ("machine", 120), ("cheeses", 5)]
# Set starting weight to 0
weight = 0
# init an empty list that we can append to as we iterate.
items = []

# For each tuple(cargo) in the List(manifest)
for cargo in manifest:
    # Check the existing weight plus the weight of the current tuple
    if weight + cargo[1] >= 100:
        # If the existing weight plus the weight of the current tuple exceeds 100 skip this tuple and goto the next one.
        continue
    else:
        # If the existing weight plus the weight of the current tuple does NOT exceed 100, append that tuple to the Items List.
        items.append(cargo[0])
        # Increase the current ships weight by the weight of the item we just added.
        weight += cargo[1]

# Print the total weight of the boat
print(weight)
# Print all the items loaded on the boat.
print(items)