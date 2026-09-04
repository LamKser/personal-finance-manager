from src.logger import logger

from dotenv import load_dotenv

load_dotenv()
logger()


from src.agent import LangGraphAgent
agent = LangGraphAgent()

# from IPython.display import Image, display
# from src.utils.visualization.graph_visualize import GraphVisualization
# display(Image(GraphVisualization().visualize_png(agent.graph)))

history = [
    # "tool Tối Thứ Ba mua cà phê ở Ministop, trả tiền mặt 18 nghìn."
    # "(tool) Đếm số giao dịch của Tháng 2"
    "Liệt kê giao dịch vào ngày 12 tháng 5 bằng chuyển khoản",
    # "Đếm toàn bộ số lượng giao dịch"
    # "Xin chào"
]
a = agent.invoke_graph(history)