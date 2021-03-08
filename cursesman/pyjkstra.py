def listToGraph(l):
    nodes = {}
    for y in range(len(l)):
        for x in range(len(l[0])):
            associated_nodes = {} 
            node_key = str(x)+','+str(y)
            if x > 0 and l[y][x-1] != 0:
               associated_nodes[(str(x-1)+','+str(y))] = 1

            if y > 0 and l[y-1][x] != 0:
               associated_nodes[(str(x)+','+str(y-1))] = 1 

            if x < len(l[0]) - 1 and l[y][x+1] != 0:
               associated_nodes[(str(x+1)+','+str(y))] = 1 

            if y < len(l) - 1 and l[y+1][x] != 0:
               associated_nodes[(str(x)+','+str(y+1))] = 1 
            
            #if x > 0 and y > 0 and l[y-1][x-1] != 0:
            #   associated_nodes[(str(x-1)+','+str(y-1))] = 1 

            #if x < len(l[0]) - 1 and y < len(l) - 1 and l[y+1][x+1] != 0:
            #   associated_nodes[(str(x+1)+','+str(y+1))] = 1 

            #if x < len(l[0]) - 1 and y > 0 and l[y-1][x+1] != 0:
            #   associated_nodes[(str(x+1)+','+str(y-1))] = 1 

            #if x > 0 and y < len(l) - 1 and l[y+1][x-1]:
            #   associated_nodes[(str(x-1)+','+str(y+1))] = 1 
            nodes[node_key] = associated_nodes
    return nodes

def find_path_for_graph(graph, start, end):
    initial = start
    path = {}
    adj_node = {}
    queue = []
    for node in graph:
        path[node] = float("inf")
        adj_node[node] = None
        queue.append(node)
        
    path[initial] = 0
    while queue:
        # find min distance which wasn't marked as current
        key_min = queue[0]
        min_val = path[key_min]
        for n in range(1, len(queue)):
            if path[queue[n]] < min_val:
                key_min = queue[n]  
                min_val = path[key_min]
        cur = key_min
        queue.remove(cur)
        
        for i in graph[cur]:
            alternate = graph[cur][i] + path[cur]
            if path[i] > alternate:
                path[i] = alternate
                adj_node[i] = cur
                
    final_path = []            
    x = end

    while True:
        x = adj_node[x]
        if x is None:
            break
        final_path.append(x) 
    return final_path

def dijkstra(l, start, end):
    graph = listToGraph(l)
    s = str(start[0]) + ',' + str(start[1])
    e = str(end[0]) + ',' + str(end[1])
    path = find_path_for_graph(graph, s, e)
    return_path = [] 
    for p in path:
        ps = p.split(',')
        ps = [int(x) for x in ps]
        return_path.append(ps)
    print(return_path) 
    return return_path


