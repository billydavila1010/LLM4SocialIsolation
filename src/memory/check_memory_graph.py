
from src.memory.memory_graph import TimeIndexedMemoryGraph

if __name__ == '__main__':
    memory_graph = TimeIndexedMemoryGraph(None)
    memory_graph.load('./xxx.json')
    for n in memory_graph.time_indexed_memory_chain:
        print(n)