from intro_algo.part6.graph import *
from intro_algo.part6.sssp import *
import os

class TestSSSP:

    def test_graph_22_4(self):
        test_file = os.path.join(os.path.dirname(__file__), 'test_data', '24_4.txt')
        g = GraphFileParser(test_file).parse_graph()
        result = BellmanFord(CostWeightMap())(g, 's')

        # 校验计算结果
        assert result.success == True
        expect_path = Path(g).generate_from_link_ids(['sy', 'yx', 'xt', 'tz'], -2)
        result_path = Path(g).generate_from_path_tree(result, 'z')

        assert str(expect_path) == str(result_path)
        assert expect_path == result_path
