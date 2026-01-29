positions = [ 
    ('Bob',  0.0, 21.0), 
    ('Cat',  2.5, 13.1), 
    ('Dog', 33.0,  1.2) 
]
def minmax(objects): 
    minx = 1e20 
    miny = 1e20 
    for obj in objects: 
        name, x, y = obj 
        if x < minx:  
            minx = x 
        if y < miny: 
            miny = y 
    return minx, miny 
  
x, y = minmax(positions) 
print(x, y)
#fait avec l'aide de la correction