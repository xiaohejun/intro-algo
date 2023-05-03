from abc import ABC
import math

class Node:
    def __init__(self, id, **attr) -> None:
        self._id = id
        self._attr = attr

        # 出边
        self._out_links = {}

        # 入边
        self._in_links = {}
    
    @property
    def id(self):
        return self._id
    
    @property
    def attr(self):
        return self._attr

    @property
    def out_links(self):
        return self._out_links
    
    @property
    def in_links(self):
        return self._in_links
    
    def add_out_link(self, link):
        assert link.src_id == self.id

        self.out_links[link.id] = link
    
    def add_in_link(self, link):
        assert link.dst_id == self.id

        self.in_links[link.id] = link
    
    def add_link(self, link):
        if link.src_id == self.id:
            self.add_out_link(link)
        
        if link.dst_id == self.id:
            self.add_in_link(link)
    
    def __repr__(self) -> str:
        return f'''
            Node:id {self.id},attr {self.attr}
            \nout_links {self.out_links}
            \nin_links {self.in_links}'''
    
class Link:
    def __init__(self, id: str, src_id, dst_id, **attr) -> None:
        self._id = id
        self._src_id = src_id
        self._dst_id = dst_id
        self._attr = attr
    
    @property
    def id(self):
        return self._id
    
    @property
    def src_id(self):
        return self._src_id
    
    @property
    def dst_id(self):
        return self._dst_id

    @property
    def attr(self):
        return self._attr
    
    def __repr__(self) -> str:
        return f'Link:id {self.id},src_id {self.src_id},dst_id {self.dst_id},attr {self.attr}'

class WeightMapBase(ABC):
    def weight(self, obj):
        raise AssertionError('must be implemented by subclass')
    
    def inf(self):
        raise AssertionError('must be implemented by subclass')
    
    def zero(self):
        raise AssertionError('must be implemented by subclass')

class CostWeightMap(WeightMapBase):
    def weight(self, obj):
        return int(obj.attr['cost'])
    
    def inf(self):
        return math.inf

    def zero(self):
        return 0


class Graph:

    def __init__(self):
        self._nodes = {}
        self._links = {}
    
    @property
    def nodes(self):
        return self._nodes
    
    @property
    def links(self):
        return self._links
    
    def add_link(self, link: Link):
        # 把link加到图中
        self._links[link.id] = link

        # 把link加到源节点下
        src_node = self.nodes[link.src_id]
        if src_node != None:
            src_node.add_link(link)
    
    def add_node(self, node: Node):
        self._nodes[node.id] = node
    
    def add(self, obj):
        if obj == None:
            return

        funcs = {
            Node: self.add_node,
            Link: self.add_link
        }

        for clazz, func in funcs.items():
            if isinstance(obj, clazz):
                func(obj)
    
    # def get_node(self, id):
    #     return self._nodes[id]

    # def get_link(self, id):
    #     return self._links[id]
    
    def __repr__(self) -> str:
        return f'nodes: {self.nodes}, links: {self.links}'

class GraphAttrParser:
    def __init__(self, out_obj_class, prefix, must_have=[]) -> None:
        self._out_obj_class = out_obj_class
        self._prefix = prefix
        self._must_have = must_have
    
    def parse_by_prefix(self, line):
        '''
        把以下格式的字符串转换成字典
        输入: prefix:attr1 xx,attr2 yy,attr3 zz 
        输出: {
            'attr1': xx,
            'attr2': yy,
            'attr3': zz
        }
        '''
        attrs = line.removeprefix(self.prefix).rstrip().split(',')

        # 解析 attrs
        result = {}
        sep_ch = ' '
        for attr in attrs:
            k, sep, v = attr.partition(sep_ch)
            if sep != sep_ch:
                raise ValueError(f'wrong fromat, parse failed==>{line}')
            result[k] = v

        return result
    
    @property
    def prefix(self):
        return self._prefix
    
    @property
    def out_obj_class(self):
        return self._out_obj_class
    
    @property
    def must_have(self):
        return self._must_have
    
    def parse(self, line):
        if self.prefix not in line:
            return None

        # 校验必须配置的值
        attrs =  self.parse_by_prefix(line)
        for attr in self.must_have:
            if attr not in attrs:
                raise ValueError()
        
        return self.out_obj_class(**attrs)


class GraphFileParser:
    parsers = [
        GraphAttrParser(Node, 'UpdateNode:', ['id']),
        GraphAttrParser(Link, 'UpdateLink:', ['id', 'src_id', 'dst_id'])
    ]

    def __init__(self, file) -> None:
        self._file = file
    
    @staticmethod
    def parse_line(line):
        for parser in GraphFileParser.parsers:
            obj = parser.parse(line)
            if obj != None:
                return obj
        return None

    def parse_graph(self):
        g = Graph()
        file = open(self._file)
        line = file.readline()
        while line:
            # 解析一行信息，然后把解析到的对象加入到图里面
            g.add(GraphFileParser.parse_line(line))
            line = file.readline() 
        return g

