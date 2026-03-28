import tensorflow as tf
import numpy as np
import cv2
import os
from typing import List, Tuple

class FaceNet:#定义一个类
    def __init__(self, model_path: str):

        self.model_path = model_path#保存模型文件路径到实例属性，后续加载模型时使用
        self.graph = tf.Graph()#创建tensorflow计算图，管理模型的计算流程
        self.session = tf.compat.v1.Session(graph=self.graph)

        self._load_model()#调用内部方法，加载模型到计算图

        self.input_tensor = self.graph.get_tensor_by_name('input:0')
        self.output_tensor = self.graph.get_tensor_by_name('embeddings:0')
        self.phase_train_tensor = self.graph.get_tensor_by_name('phase_train:0')

    def _load_model(self):

        try:#确保操作在计算图中执行
            with self.graph.as_default():
                with tf.io.gfile.GFile(self.model_path, 'rb') as f:#创建对象，用于解析模型中的数据
                    graph_def = tf.compat.v1.GraphDef()
                    graph_def.ParseFromString(f.read())#将解析后的模型导入计算图中，name表示默认命名空间
                    tf.import_graph_def(graph_def, name='')
            print(f"模型 {self.model_path} 加载成功")#加载成功提示
        except Exception as e:#捕获加载过程中的异常
            print(f"模型加载失败: {e}")#打印信息错误
            raise#失败

    @staticmethod
    def preprocess_image(image: np.ndarray) -> np.ndarray:

        if image is None or image.size == 0:#检查图像是否为空
            raise ValueError("输入图像为空")#输入尺寸
        image = cv2.resize(image, (160, 160))#归一化：减均值，除标准差
        image = (image - 127.5) / 127.5#扩展维度，变成（1，160，160，3），适配模型输入
        return np.expand_dims(image, axis=0)

    def get_face_embedding(self, image: np.ndarray) -> np.ndarray:#先将图像做预处理
        preprocessed_image = self.preprocess_image(image)#通过会话执行模型，喂入预处理后的图像，指定输出
        embedding = (self.session.run(
            self.output_tensor,
            feed_dict={
                self.input_tensor: preprocessed_image,
                self.phase_train_tensor: False
            }
        ))
        return embedding[0]#去掉batch维度（因为输入时（1，x），输出也是（1，特征维度））

    @staticmethod
    def euclidean_distance(embedding1: np.ndarray, embedding2: np.ndarray) -> float:#欧式距离公式
        return np.sqrt(np.sum(np.square(embedding1 - embedding2)))

    @staticmethod
    def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:#余弦相似度公式
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

    def compare_faces(self, image_path1: str, image_path2: str, threshold: float = 1.1) -> Tuple[float, float, bool]:#用openCV读取2张图片
        image1 = cv2.imread(image_path1)
        image2 = cv2.imread(image_path2)#检查图片是否读取成功

        if image1 is None:
            raise FileNotFoundError(f"无法读取图像: {image_path1}")
        if image2 is None:
            raise FileNotFoundError(f"无法读取图像: {image_path2}")
        #提取2张图片的人脸特征
        embedding1 = self.get_face_embedding(image1)
        embedding2 = self.get_face_embedding(image2)
        #计算欧式距离，余弦相似度
        distance = self.euclidean_distance(embedding1, embedding2)
        similarity = self.cosine_similarity(embedding1, embedding2)

        is_same_person = distance < threshold#通过欧式距离和法制判断是否为同一个人

        return distance, similarity, is_same_person#返回对比结果


if __name__ == "__main__":
    #初始化FaceNet对象，传入模型文件路径
    model = FaceNet('_001.pb')

    try:#调用compare— face对比2张图片，拿到距离，相似度，结果是不是同一个人
        distance, similarity, is_same = model.compare_faces("a_002.jpg", "a_003.jpg")
        #distance, similarity, is_same = model.compare_faces("a_002.jpg", "a_003.jpg")
        print(f"欧氏距离: {distance:.4f}")
        print(f"余弦相似度: {similarity:.4f}")
        print(f"是否为同一人: {'是' if is_same else '否'}")#输出中文提示

    except Exception as e:#驳货执行过程中的异常
        print(f"处理过程中发生错误: {e}")#打印错误信息

cv2.destroyAllWindows()