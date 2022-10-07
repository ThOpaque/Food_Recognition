import unittest
import torch

from darknet import YoloV1

class TestDarknet(unittest.TestCase):
    def __init__(self, TestDarknet) -> None:
        super().__init__(TestDarknet)
        self.size = 448
        self.S = 7
        self.B = 2
        self.C = 8
        self.channel_img = 3

    def test_darknet(self):
        BATCH_SIZE = 64
        model = YoloV1(in_channels=self.channel_img, S=self.S, C=self.C, B=self.B)
        img_test = torch.rand(BATCH_SIZE, self.channel_img, self.size, self.size)
        output = model(img_test)
        
        self.assertEqual(output.shape, torch.Size([BATCH_SIZE, self.S, self.S, self.B*(4+1)+self.C]))


if __name__ == "__main__":
    unittest.main()