from .graph import Graph
from .graph import Link
from .graph import WeightMapBase

class Path:

    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self._links = []
        self._distance = None
    
    def generate_from_path_tree(self, path_tree, dst_id):
        """从路径树中生成路径

        Args:
            dst_id (Any): 目的地的key

        Returns:
            list: 路径
        """
        if not path_tree.success:
            raise ValueError('The current result calculation failed')
        
        links = []
        cur_id = dst_id
        while cur_id != path_tree.src_id:
            link = path_tree.prev[cur_id]
            if link != self._graph.links[link.id]:
                raise ValueError('path tree and graph not match')
            links.append(link)
            cur_id = link.src_id
        links.reverse()

        self._links = links
        self._distance = path_tree.distance[dst_id]

        return self
    
    def generate_from_link_ids(self, link_ids, distance):
        self._distance = distance
        self._links = [self._graph.links[link_id] for link_id in link_ids]

        return self
    
    @property
    def links(self):
        return self._links
    
    @property
    def graph(self):
        return self.graph
    
    @property
    def distance(self):
        return self._distance
    
    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False

        if self._distance != other.distance:
            return False
        
        if self._links != other.links:
            return False
        
        return True
    
    def __str__(self):
        return '->'.join(link.id for link in self.links)

class ShortestPathsTree:

    def __init__(self, src_id) -> None:
        self._src_id = src_id
        self._distance = {}
        self._prev = {}
        self._success = False
    
    @property
    def src_id(self):
        return self._src_id
    
    @property
    def distance(self):
        return self._distance
    
    @property
    def prev(self):
        return self._prev
    
    @property
    def success(self):
        return self._success

    @success.setter
    def success(self, val):
        self._success = val

    def initialize_single_source(self, g: Graph, s, weight_map: WeightMapBase):
        """初始化

        Args:
            g (Graph): 要计算的图
            s (Any): 源节点id
            weight_map (WeightMapBase): 路径权重的函数
        """

        # 将图中所有结点的距离设置成inf 
        for k in g.nodes:
            self.distance[k] = weight_map.inf()
        
        # 源结点的距离初始化成0
        self.distance[s] = weight_map.zero()
    

class SSSP:
    """single sources shortest path
    求解单源最短路径 
    """
    
    def __init__(self, weight_map: WeightMapBase) -> None:
        self._weight_map = weight_map
    
    def __call__(self, g: Graph, s) -> ShortestPathsTree:
        """计算单源最短路径

        Args:
            g (Graph): 要计算单源最短路径的图
            s (Any): 源结点id

        Raises:
            AssertionError: 该方法必须由子类实现

        Returns:
            ShortestPathsTree: 以s为根的最短路径树
        """
        raise AssertionError('Must be implemented by a subclass')
    
    @property
    def weight_map(self):
        return self._weight_map
    
    def relax(self, link: Link, result: ShortestPathsTree):
        """用边作松弛操作

        Args:
            link (Link): 边
            result (ShortestPathsTree): 要更新的结果
        """
        # 尝试使用当前的link的权重来松弛到目的结点的距离
        tmp = result.distance[link.src_id] + self.weight_map.weight(link)
        # 结果更好的话，减小最短路径估计值
        if result.distance[link.dst_id] > tmp:
            result.distance[link.dst_id] = tmp
            result.prev[link.dst_id] = link

class BellmanFord(SSSP):

    def __call__(self, g: Graph, s) -> ShortestPathsTree:
        """考虑任意从源结点s可以到达的结点v, 设p=<v0, v1, ..., vk>为从源结点s到
        结点v之间的任意一条最短路径, 这里v0 = s, vk = v。因为最短路径都是简单路径,
        p最多包含|V| - 1条边, 因此|k| <= |V| - 1. BellmanFord求最短路径时每次
        松弛所有的|E|条边. 一共松弛|V| - 1次, 在第i次松弛时, 这里的i=1, 2, ..., k,
        被松弛的边包含边 <vi-1, vi>. 根据路径松弛性质, v.d = vk.d = delt(s, vk) = delt(s, v)
        """
        result = ShortestPathsTree(s)
        # 初始化
        result.initialize_single_source(g, s, self.weight_map)

        # 用图中的每一条边松弛|V| - 1次
        for i in range(len(g.nodes) -  1):
            for _, link in g.links.items():
                self.relax(link, result)
            
        # 如果有负权重的环则最短路计算失败
        for _, link in g.links.items():
            if result.distance[link.dst_id] > result.distance[link.src_id] + self.weight_map.weight(link):
                result.success = False
                return

        # 否则：计算成功
        result.success = True

        return result
