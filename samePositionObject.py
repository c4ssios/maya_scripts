visited = set()
duplicates = set()

for item in cmds.ls("*GE?"):
    pos = tuple( cmds.xform(item, q=True, ws=True, t=True) )
    
    if pos in visited:
        duplicates.add(item)
    else:
        visited.add(pos)
        
        
cmds.select(list(duplicates))
